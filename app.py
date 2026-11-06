
import os
import uuid

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, abort
)

from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

from models import db, User
from document_model import Document, DocumentPermission, AuditLog


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-change-before-deployment"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///trustvault.db"
)

app.config["UPLOAD_FOLDER"] = os.environ.get(
    "UPLOAD_FOLDER", os.path.join(app.root_path, "uploads")
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt", "docx"}

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()
    print("TrustVault database is ready!")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 12:
            flash("Enter valid details. Password must be at least 12 characters.")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("register"))

        user = User(name=name, email=email, role="viewer")
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        flash(
            "Password reset by email is currently unavailable. "
            "Please contact the administrator."
        )
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/dashboard")
@login_required
def dashboard():
    documents = Document.query.filter_by(
        owner_id=current_user.id
    ).all()

    shared_documents = Document.query.join(
        DocumentPermission,
        Document.id == DocumentPermission.document_id
    ).filter(
        DocumentPermission.user_id == current_user.id,
        (DocumentPermission.can_read == True) |
        (DocumentPermission.can_edit == True)
    ).all()

    shared_permissions = {}

    for doc in documents:
        permissions = DocumentPermission.query.filter_by(
            document_id=doc.id
        ).all()

        shared_permissions[doc.id] = [
            (permission, db.session.get(User, permission.user_id))
            for permission in permissions
        ]

    return render_template(
        "dashboard.html",
        documents=documents,
        shared_documents=shared_documents,
        shared_permissions=shared_permissions
    )


@app.route("/search")
@login_required
def search_documents():
    keyword = request.args.get("name", "").strip()
    category = request.args.get("category", "").strip()
    owner_email = request.args.get("owner", "").strip().lower()
    date = request.args.get("date", "").strip()

    query = Document.query.join(
        User, Document.owner_id == User.id
    ).filter(
        (Document.owner_id == current_user.id) |
        (Document.id.in_(
            db.session.query(DocumentPermission.document_id).filter(
                DocumentPermission.user_id == current_user.id,
                (DocumentPermission.can_read == True) |
                (DocumentPermission.can_edit == True)
            )
        ))
    )

    if keyword:
        query = query.filter(Document.filename.ilike(f"%{keyword}%"))

    if category:
        query = query.filter(Document.category.ilike(f"%{category}%"))

    if owner_email:
        query = query.filter(User.email.ilike(f"%{owner_email}%"))

    if date:
        try:
            from datetime import datetime
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(
                db.func.date(Document.created_at) == selected_date
            )
        except ValueError:
            flash("Invalid date format.")

    documents = query.order_by(Document.created_at.desc()).all()

    return render_template(
        "search.html",
        documents=documents,
        keyword=keyword,
        category=category,
        owner_email=owner_email,
        date=date
    )


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        category = request.form.get("category", "").strip()

        if not file or file.filename == "":
            flash("Please select a file.")
            return redirect(url_for("upload"))

        if not allowed_file(file.filename):
            flash("File type not allowed.")
            return redirect(url_for("upload"))

        original_name = secure_filename(file.filename)
        stored_name = str(uuid.uuid4()) + "_" + original_name

        file.save(
            os.path.join(app.config["UPLOAD_FOLDER"], stored_name)
        )

        document = Document(
            filename=original_name,
            stored_name=stored_name,
            category=category,
            owner_id=current_user.id
        )

        db.session.add(document)
        db.session.flush()

        db.session.add(AuditLog(
            user_id=current_user.id,
            document_id=document.id,
            action="UPLOAD",
            details="Document uploaded successfully"
        ))

        db.session.commit()

        flash("Document uploaded successfully.")
        return redirect(url_for("dashboard"))

    return render_template("upload.html")


@app.route("/download/<int:document_id>")
@login_required
def download(document_id):
    document = db.session.get(Document, document_id)

    if not document:
        db.session.add(AuditLog(
            user_id=current_user.id,
            action="DOWNLOAD_DENIED",
            details=f"Document {document_id} not found"
        ))
        db.session.commit()
        abort(404)

    permission = DocumentPermission.query.filter_by(
        document_id=document.id,
        user_id=current_user.id
    ).first()

    allowed = (
        document.owner_id == current_user.id
        or (
            permission is not None
            and (permission.can_read or permission.can_edit)
        )
    )

    if not allowed:
        db.session.add(AuditLog(
            user_id=current_user.id,
            document_id=document.id,
            action="DOWNLOAD_DENIED",
            details="User has no read permission"
        ))
        db.session.commit()
        abort(403)

    db.session.add(AuditLog(
        user_id=current_user.id,
        document_id=document.id,
        action="DOWNLOAD",
        details="Document downloaded successfully"
    ))
    db.session.commit()

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        document.stored_name,
        as_attachment=True,
        download_name=document.filename
    )


@app.route("/share/<int:document_id>", methods=["POST"])
@login_required
def share_document(document_id):
    document = db.session.get(Document, document_id)

    if not document or document.owner_id != current_user.id:
        abort(403)

    email = request.form.get("email", "").strip().lower()
    can_read = request.form.get("can_read") == "on"
    can_edit = request.form.get("can_edit") == "on"

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found.")
        return redirect(url_for("dashboard"))

    if user.id == current_user.id:
        flash("You already own this document.")
        return redirect(url_for("dashboard"))

    if not can_read and not can_edit:
        flash("Select at least one permission.")
        return redirect(url_for("dashboard"))

    permission = DocumentPermission.query.filter_by(
        document_id=document.id,
        user_id=user.id
    ).first()

    if permission is None:
        permission = DocumentPermission(
            document_id=document.id,
            user_id=user.id
        )
        db.session.add(permission)

    permission.can_read = can_read
    permission.can_edit = can_edit

    db.session.add(AuditLog(
        user_id=current_user.id,
        document_id=document.id,
        action="PERMISSION_GRANTED",
        details=f"Access granted to {email}"
    ))

    db.session.commit()

    flash("Document permission updated successfully.")
    return redirect(url_for("dashboard"))


@app.route("/revoke/<int:document_id>/<int:user_id>", methods=["POST"])
@login_required
def revoke_access(document_id, user_id):
    document = db.session.get(Document, document_id)

    if not document or document.owner_id != current_user.id:
        abort(403)

    permission = DocumentPermission.query.filter_by(
        document_id=document_id,
        user_id=user_id
    ).first()

    if not permission:
        abort(404)

    db.session.add(AuditLog(
        user_id=current_user.id,
        document_id=document_id,
        action="PERMISSION_REVOKED",
        details=f"Access revoked from user {user_id}"
    ))

    db.session.delete(permission)
    db.session.commit()

    flash("Access revoked successfully.")
    return redirect(url_for("dashboard"))


@app.route("/delete/<int:document_id>", methods=["POST"])
@login_required
def delete_document(document_id):
    document = db.session.get(Document, document_id)

    if not document or document.owner_id != current_user.id:
        abort(403)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        document.stored_name
    )

    db.session.add(AuditLog(
        user_id=current_user.id,
        document_id=document.id,
        action="DELETE",
        details="Document deleted successfully"
    ))

    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(document)
    db.session.commit()

    flash("Document deleted successfully.")
    return redirect(url_for("dashboard"))


@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        abort(403)

    logs = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).all()

    activities = [
        (log, db.session.get(User, log.user_id))
        for log in logs
    ]

    return render_template(
        "admin.html",
        activities=activities
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False)
