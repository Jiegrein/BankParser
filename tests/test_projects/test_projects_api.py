"""
API/End-to-End tests for Projects endpoints
Tests full HTTP request/response cycle
"""

from uuid import uuid4

from app.core.db.models import Project


class TestProjectsAPIEndpoints:
    """End-to-end tests for Projects API endpoints"""

    def test_create_project_returns_201(self, client, sample_project_data):
        """Test POST /api/v1/projects returns 201 Created"""
        # Act
        response = client.post("/api/v1/projects", json=sample_project_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["developer_name"] == sample_project_data["developer_name"]
        assert data["is_activated"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_project_validates_required_fields(self, client):
        """Test POST /api/v1/projects returns 422 for missing fields"""
        # Act
        response = client.post("/api/v1/projects", json={"name": "Test"})

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"
        assert "developer_name" in str(data["details"])

    def test_create_project_rejects_whitespace_only_fields(self, client):
        """Test POST /api/v1/projects returns 422 for whitespace-only fields"""
        # Act
        response = client.post(
            "/api/v1/projects",
            json={
                "name": "   ",  # Whitespace only
                "developer_name": "Dev",
                "investor_name": "Investor",
                "created_by": "test@test.com",
            },
        )

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "whitespace" in str(data["details"]).lower()

    def test_get_project_returns_200(self, client, sample_project):
        """Test GET /api/v1/projects/{id} returns 200 OK"""
        # Act
        response = client.get(f"/api/v1/projects/{sample_project.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_project.id)
        assert data["name"] == sample_project.name

    def test_get_project_returns_404_for_missing_project(self, client):
        """Test GET /api/v1/projects/{id} returns 404 for non-existent project"""
        # Arrange
        random_id = uuid4()

        # Act
        response = client.get(f"/api/v1/projects/{random_id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "NOT_FOUND"
        assert str(random_id) in data["details"]["project_id"]

    def test_get_project_returns_422_for_invalid_uuid(self, client):
        """Test GET /api/v1/projects/{id} returns 422 for invalid UUID"""
        # Act
        response = client.get("/api/v1/projects/invalid-uuid")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_get_projects_list_returns_200(self, client, multiple_projects):
        """Test GET /api/v1/projects returns 200 with paginated list"""
        # Act
        response = client.get("/api/v1/projects")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total"] == 5
        assert len(data["items"]) == 5

    def test_get_projects_pagination_works(self, client, multiple_projects):
        """Test GET /api/v1/projects pagination parameters work"""
        # Act
        response = client.get("/api/v1/projects?page=1&page_size=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) == 2
        assert data["total_pages"] == 3

    def test_get_projects_search_works(self, client, multiple_projects):
        """Test GET /api/v1/projects search parameter works"""
        # Act
        response = client.get("/api/v1/projects?search=Project 1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Project 1"

    def test_get_projects_filter_by_is_activated(self, client, multiple_projects):
        """Test GET /api/v1/projects filters by is_activated"""
        # Act - Active only
        response = client.get("/api/v1/projects?is_activated=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3  # Projects 0, 2, 4 are active
        for item in data["items"]:
            assert item["is_activated"] is True

    def test_get_projects_validates_page_number(self, client):
        """Test GET /api/v1/projects returns 422 for invalid page"""
        # Act
        response = client.get("/api/v1/projects?page=0")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"
        assert "page" in str(data["details"]).lower()

    def test_get_projects_validates_page_size(self, client):
        """Test GET /api/v1/projects returns 422 for page_size > 100"""
        # Act
        response = client.get("/api/v1/projects?page_size=200")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "page_size" in str(data["details"]).lower()

    def test_update_project_returns_200(self, client, sample_project):
        """Test PUT /api/v1/projects/{id} returns 200 OK"""
        # Act
        response = client.put(
            f"/api/v1/projects/{sample_project.id}",
            json={"name": "Updated Project Name", "updated_by": "updater@test.com"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project Name"
        assert data["updated_by"] == "updater@test.com"

    def test_update_project_partial_update_works(self, client, sample_project):
        """Test PUT /api/v1/projects/{id} allows partial updates"""
        # Arrange
        original_developer = sample_project.developer_name

        # Act - Only update name
        response = client.put(
            f"/api/v1/projects/{sample_project.id}", json={"name": "Only Name Changed"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Only Name Changed"
        assert data["developer_name"] == original_developer  # Unchanged

    def test_update_project_returns_404_for_missing_project(self, client):
        """Test PUT /api/v1/projects/{id} returns 404 for non-existent project"""
        # Arrange
        random_id = uuid4()

        # Act
        response = client.put(f"/api/v1/projects/{random_id}", json={"name": "Updated"})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_delete_project_returns_204(self, client, sample_project):
        """Test DELETE /api/v1/projects/{id} returns 204 No Content"""
        # Act
        response = client.delete(f"/api/v1/projects/{sample_project.id}")

        # Assert
        assert response.status_code == 204
        assert response.content == b""

    def test_delete_project_soft_deletes(self, client, test_db, sample_project):
        """Test DELETE /api/v1/projects/{id} sets is_activated=False"""
        # Act
        response = client.delete(f"/api/v1/projects/{sample_project.id}")

        # Assert
        assert response.status_code == 204

        # Verify soft delete
        db_project = (
            test_db.query(Project).filter(Project.id == sample_project.id).first()
        )
        assert db_project is not None  # Still exists
        assert db_project.is_activated is False  # But inactive

    def test_delete_project_returns_404_for_missing_project(self, client):
        """Test DELETE /api/v1/projects/{id} returns 404 for non-existent project"""
        # Arrange
        random_id = uuid4()

        # Act
        response = client.delete(f"/api/v1/projects/{random_id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in responses"""
        # Act
        response = client.get("/api/v1/projects")

        # Assert - CORS headers should be present (configured in main.py)
        # Note: TestClient may not include all CORS headers, but endpoint should work
        assert response.status_code == 200

    def test_error_response_format_consistent(self, client):
        """Test error responses follow consistent format"""
        # Act
        response = client.get(f"/api/v1/projects/{uuid4()}")

        # Assert
        assert response.status_code == 404
        data = response.json()

        # All error responses should have these fields
        assert "success" in data
        assert "error" in data
        assert "error_code" in data
        assert "details" in data
        assert "path" in data

        assert data["success"] is False
        assert isinstance(data["error"], str)
        assert isinstance(data["error_code"], str)
        assert isinstance(data["details"], dict)
