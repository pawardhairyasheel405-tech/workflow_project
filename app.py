from flask import Flask, render_template, redirect, url_for, request, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import re
from datetime import datetime
from database import save_comment
app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOCS_FOLDER'] = 'static/docs'
db = SQLAlchemy(app)

from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped


# --- Role permissions and workflow ---
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

ROLE_PERMS = {
    'engineer': ['view', 'comment', 'approve', 'forward', 'upload'],
    'deputy_engineer': ['view', 'comment', 'approve', 'forward'],
    'finance': ['view', 'comment', 'approve', 'forward'],
    'ceo': ['view', 'comment', 'approve', 'reject']
}

FLOW = {
    'engineer': 'deputy_engineer',
    'deputy_engineer': 'finance',
    'finance': 'ceo',
    'ceo': 'completed'
}


# utilities
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_user():
    """Return the current logged-in User model or None."""
    username = session.get('user')
    if not username:
        return None
    return User.query.filter_by(username=username).first()


def _normalize_role_key(role_str: str) -> str:
    """Normalize a role string to the ROLE_PERMS key format.

    Examples:
      'Deputy Engineer' -> 'deputy_engineer'
      'Finance' -> 'finance'
      'CEO' -> 'ceo'
    """
    if not role_str:
        return ''
    key = re.sub(r"\W+", '_', role_str.strip().lower())
    return key


def _human_role_from_key(key: str) -> str:
    """Convert a normalized role key back to a human-friendly role name.

    Keeps special-case for 'ceo' -> 'CEO'.
    """
    if not key:
        return ''
    if key == 'ceo':
        return 'CEO'
    return key.replace('_', ' ').title()


def requires_permission(action):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'unauthorized', 'message': 'Login required'}), 401
            # normalize role to ROLE_PERMS key format
            role_key = _normalize_role_key(user.role)
            if role_key not in ROLE_PERMS or action not in ROLE_PERMS.get(role_key, []):
                return jsonify({'error': 'forbidden', 'message': 'You lack permission for this action'}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ---------- MODELS ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    role = db.Column(db.String(50))  # Engineer, Deputy, Finance, CEO

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    status = db.Column(db.String(50), default="Pending")
    current_role = db.Column(db.String(50), default="Engineer")


    # Role permission mapping
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=True)
    role = db.Column(db.String(80), nullable=False)        # e.g. "Engineer", "Deputy Engineer"
    comment_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "role": self.role,
            "comment": self.comment_text,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
    
def save_comment(document_id, role, comment_text):
    """
    Save a comment to the DB.
    - document_id: int or None
    - role: string (e.g. "Engineer")
    - comment_text: string
    Returns the created Comment instance.
    """
    if not comment_text or not role:
        raise ValueError("role and comment_text are required")

    c = Comment(
        document_id=document_id,
        role=role,
        comment_text=comment_text
    )
    db.session.add(c)
    db.session.commit()
    return c

# ---------- ROUTES ----------
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


from flask import request, redirect
import os

# SHOW UPLOAD PAGE (GET)
@app.route("/upload", methods=["GET"])
def upload_page():
    return render_template("upload.html")


# HANDLE ACTUAL UPLOAD (POST)
@app.route("/upload_document", methods=["POST"])
def upload_document():
    if "document" not in request.files:
        return "No file received!"

    pdf = request.files["document"]

    if pdf.filename == "":
        return "No selected file"

    save_path = os.path.join("static/docs", "sample.pdf")
    pdf.save(save_path)

    return redirect(url_for("dashboard"))





@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user'] = user.username
            session['user_id'] = user.id
            session['role'] = user.role

            # Redirect based on role
            role = (user.role or '').strip()
            if role == 'Deputy Engineer':
                return redirect(url_for('deputy_dashboard'))
            elif role == 'Finance':
                return redirect(url_for('finance_dashboard'))
            elif role == 'CEO':
                return redirect(url_for('ceo_dashboard'))
            return redirect(url_for('dashboard'))

        # ❌ wrong credentials → reload login page
        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route("/dashboard")
@login_required
@requires_permission('view')
def dashboard():
    comments = [
        {"user": "Engineer1", "text": "Checked document", "time": "2025-11-16"},
        {"user": "Deputy", "text": "Forwarded", "time": "2025-11-17"},
    ]

    return render_template(
        "dashboard.html",
        document_filename="sample.pdf",  
        comments=comments,
        role=session.get("role")
    )


@app.route("/engineer_comment", methods=["POST"])
def engineer_comment():
    comment = request.form.get("comment")
    save_comment("Engineer", comment)
    return redirect("/engineer_dashboard")

@app.route('/add_comment/<int:doc_id>', methods=['POST'])
@login_required
@requires_permission('comment')
def add_comment(doc_id):
    # Accepts JSON: { "comment": "text here" }
    data = request.get_json() or request.form
    comment = (data.get('comment') or data.get('comment_text') or "").strip()
    print("HIT COMMENT ROUTE!", request.get_json(), request.form)

    if not comment:
        return jsonify({"error":"empty comment"}), 400

    # determine role from session (fallback to session['role'])
    role = session.get('role') or 'Unknown'

    try:
        c = save_comment(document_id=doc_id, role=role, comment_text=comment)
    except Exception as e:
        return jsonify({"error": "save failed", "message": str(e)}), 500

    return jsonify({"success": True, "comment": c.to_dict()})


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



@app.route('/comments/all', methods=['GET'])
@login_required
@requires_permission('view')
def get_all_comments():
    comments = Comment.query.order_by(Comment.timestamp.asc()).all()
    return jsonify([c.to_dict() for c in comments])


@app.route('/deputy_dashboard')
@login_required
@requires_permission('view')
def deputy_dashboard():
    # Query documents assigned to Deputy Engineer
    documents = Document.query.filter_by(current_role=_human_role_from_key('deputy_engineer')).all()
    return render_template('deputy_dashboard.html', documents=documents)


@app.route('/finance_dashboard')
@login_required
@requires_permission('view')
def finance_dashboard():
    # Query documents assigned to Finance
    documents = Document.query.filter_by(current_role=_human_role_from_key('finance')).all()
    return render_template('finance_dashboard.html', documents=documents)


@app.route('/ceo_dashboard')
@login_required
@requires_permission('view')
def ceo_dashboard():
    # Query documents assigned to CEO
    documents = Document.query.filter_by(current_role=_human_role_from_key('ceo')).all()
    return render_template('ceo_dashboard.html', documents=documents)






@app.route('/approve/<int:doc_id>')
@login_required
@requires_permission('approve')
def approve(doc_id):
    doc = Document.query.get(doc_id)
    if not doc:
        return "Document not found", 404

    # determine next role based on normalized FLOW mapping
    curr_key = _normalize_role_key(doc.current_role)
    next_key = FLOW.get(curr_key)
    if not next_key or next_key == 'completed':
        doc.status = 'Approved'
    else:
        # convert normalized key back to human-friendly role
        doc.current_role = _human_role_from_key(next_key)

    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route("/ceo/approve", methods=["POST"])
@login_required
def ceo_approve():
    # Save approval to DB if needed
    # document.status = "approved"
    # db.session.commit()

    return jsonify({"message": "CEO Final Approval Completed — Workflow Closed"})


@app.route("/ceo/reject", methods=["POST"])
@login_required
def ceo_reject():
    data = request.json
    reason = data.get("reason")

    # Save rejection reason to DB if needed
    # document.status = "rejected"
    # document.rejection_reason = reason
    # db.session.commit()

    return jsonify({"message": reason})


# LOGOUT REDIRECT TO LOGIN PAGE
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/get_comments")
def get_comments():
    comments = db.execute("SELECT role, comment, timestamp FROM comments ORDER BY timestamp ASC")
    
    # Convert rows to list of dict
    out = []
    for c in comments:
        out.append({
            "role": c["role"],
            "comment": c["comment"],
            "timestamp": c["timestamp"]
        })
    
    return jsonify(out)



@app.route('/docs/<filename>')
@login_required
@requires_permission('view')
def serve_doc(filename):
    """Serve PDF documents from static/docs folder."""
    return send_from_directory(app.config['DOCS_FOLDER'], filename)

# ---------- INIT DB ----------
# ---------- INIT DB ----------
initialized = False



@app.before_request
def create_tables():
    global initialized
    if not initialized:
        db.create_all()
        if not User.query.first():
            db.session.add_all([
                User(username="engineer", password="123", role=_human_role_from_key('engineer')),
                User(username="deputy", password="123", role=_human_role_from_key('deputy_engineer')),
                User(username="finance", password="123", role=_human_role_from_key('finance')),
                User(username="ceo", password="123", role=_human_role_from_key('ceo')),
            ])
            db.session.commit()
        # Seed a sample document if none exist
        if not Document.query.first():
            db.session.add(Document(filename="sample.pdf", status="Pending", current_role=_human_role_from_key('engineer')))
            db.session.commit()
        initialized = True



if __name__ == '__main__':
    app.run(debug=True)
