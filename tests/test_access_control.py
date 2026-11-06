
import os

# Use a separate database for testing
os.environ["DATABASE_URL"] = "sqlite:///test_trustvault.db"

import pytest
from app import app, db
from models import User
from document_model import Document, DocumentPermission, AuditLog


@pytest.fixture
def setup_app(tmp_path):
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        owner = User(name="Owner", email="owner@test.com", role="viewer")
        owner.set_password("OwnerPassword123")

        viewer = User(name="Viewer", email="viewer@test.com", role="viewer")
        viewer.set_password("ViewerPassword123")

        admin = User(name="Admin", email="admin@test.com", role="admin")
        admin.set_password("AdminPassword123")

        db.session.add_all([owner, viewer, admin])
        db.session.commit()

        doc = Document(
            filename="secret.txt",
            stored_name="test-secret.txt",
            category="Test",
            owner_id=owner.id
        )
        db.session.add(doc)
        db.session.commit()

        with open(os.path.join(app.config["UPLOAD_FOLDER"], doc.stored_name), "w") as f:
            f.write("secret content")

        doc_id = doc.id
        viewer_id = viewer.id

    yield {"doc_id": doc_id, "viewer_id": viewer_id}

    with app.app_context():
        db.session.remove()
        db.drop_all()


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True
    )


def test_unshared_user_cannot_download(setup_app):
    client = app.test_client()
    login(client, "viewer@test.com", "ViewerPassword123")

    response = client.get(f"/download/{setup_app['doc_id']}")

    assert response.status_code == 403

    with app.app_context():
        denied = AuditLog.query.filter_by(action="DOWNLOAD_DENIED").first()
        assert denied is not None


def test_owner_can_download(setup_app):
    client = app.test_client()
    login(client, "owner@test.com", "OwnerPassword123")

    response = client.get(f"/download/{setup_app['doc_id']}")

    assert response.status_code == 200
    assert b"secret content" in response.data


def test_non_owner_cannot_share_document(setup_app):
    client = app.test_client()
    login(client, "viewer@test.com", "ViewerPassword123")

    response = client.post(
        f"/share/{setup_app['doc_id']}",
        data={"email": "admin@test.com", "can_read": "on"}
    )

    assert response.status_code == 403


def test_non_owner_cannot_revoke_access(setup_app):
    client = app.test_client()
    login(client, "viewer@test.com", "ViewerPassword123")

    response = client.post(
        f"/revoke/{setup_app['doc_id']}/{setup_app['viewer_id']}"
    )

    assert response.status_code == 403


def test_revoked_user_cannot_download(setup_app):
    with app.app_context():
        permission = DocumentPermission(
            document_id=setup_app["doc_id"],
            user_id=setup_app["viewer_id"],
            can_read=True,
            can_edit=False
        )
        db.session.add(permission)
        db.session.commit()

    owner_client = app.test_client()
    login(owner_client, "owner@test.com", "OwnerPassword123")

    revoke_response = owner_client.post(
        f"/revoke/{setup_app['doc_id']}/{setup_app['viewer_id']}"
    )
    assert revoke_response.status_code == 302

    viewer_client = app.test_client()
    login(viewer_client, "viewer@test.com", "ViewerPassword123")

    response = viewer_client.get(f"/download/{setup_app['doc_id']}")

    assert response.status_code == 403


def test_only_admin_can_open_admin_page(setup_app):
    viewer_client = app.test_client()
    login(viewer_client, "viewer@test.com", "ViewerPassword123")

    assert viewer_client.get("/admin").status_code == 403

    admin_client = app.test_client()
    login(admin_client, "admin@test.com", "AdminPassword123")

    assert admin_client.get("/admin").status_code == 200
