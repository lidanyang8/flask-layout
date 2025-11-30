"""
API测试
"""


def test_health_check(client):
    """测试健康检查"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['status'] == 'healthy'


def test_create_user(client):
    """测试创建用户"""
    response = client.post('/api/users',
                           json={
                               'username': 'testuser',
                               'email': 'test@example.com',
                               'password': 'testpass123'
                           })
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['username'] == 'testuser'
