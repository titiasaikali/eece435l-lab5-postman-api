"""Verify real HTTP CRUD requests on an isolated DB and export Postman examples."""
import json
import os
import tempfile
import threading
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

def main():
    with tempfile.TemporaryDirectory() as temp:
        os.environ['LAB5_DATABASE'] = str(Path(temp) / 'test.db')
        from app import app
        from werkzeug.serving import make_server
        server = make_server('127.0.0.1', 0, app)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        items, results = [], []
        user = dict(name='John Doe', email='johndoe@example.com', phone='067765434567',
                    address='John Doe Street, Innsbruck', country='Austria')
        def send(method, path, body=None):
            req = Request(f'http://127.0.0.1:{server.server_port}' + path,
                          data=json.dumps(body).encode() if body is not None else None,
                          headers={'Content-Type': 'application/json'}, method=method)
            try:
                response = urlopen(req)
            except HTTPError as error:
                response = error
            with response:
                return response.status, json.loads(response.read())
        def record(name, method, path, body=None, check=None):
            status, data = send(method, path, body)
            assert status == 200, (name, status, data)
            assert check(data), (name, data)
            request = {'method': method, 'header': [],
                       'url': {'raw': '{{base_url}}' + path, 'host': ['{{base_url}}'],
                               'path': path.lstrip('/').split('/')}}
            if body is not None:
                request['header'] = [{'key': 'Content-Type', 'value': 'application/json'}]
                request['body'] = {'mode': 'raw', 'raw': json.dumps(body, indent=2),
                                   'options': {'raw': {'language': 'json'}}}
            script = ['pm.test("HTTP 200", () => pm.response.to.have.status(200));',
                      'const data = pm.response.json();']
            if method == 'POST':
                script += ['pm.environment.set("user_id", data.user_id);',
                           'pm.test("User created", () => pm.expect(data.name).to.eql("John Doe"));']
            elif method == 'PUT':
                script += ['pm.test("User updated", () => pm.expect(data.name).to.eql("Jane Doe"));']
            elif method == 'PATCH':
                script += ['pm.test("Country patched", () => pm.expect(data.country).to.eql("Lebanon"));',
                           'pm.test("Other fields preserved", () => pm.expect(data.name).to.eql("Jane Doe"));']
            elif method == 'DELETE':
                script += ['pm.test("User deleted", () => pm.expect(data.status).to.eql("User deleted successfully"));']
            elif path == '/api/users':
                script += ['pm.test("User appears in list", () => pm.expect(data.some(u => u.user_id === Number(pm.environment.get("user_id")))).to.be.true);']
            else:
                script += ['pm.test("Correct user", () => pm.expect(data.user_id).to.eql(Number(pm.environment.get("user_id"))));']
            original = json.loads(json.dumps(request))
            items.append({'name': name, 'request': request,
                          'event': [{'listen': 'test', 'script': {'type': 'text/javascript', 'exec': script}}],
                          'response': [{'name': name + ' - verified response', 'originalRequest': original,
                                        'status': 'OK', 'code': status, '_postman_previewlanguage': 'json',
                                        'header': [{'key': 'Content-Type', 'value': 'application/json'}],
                                        'cookie': [], 'body': json.dumps(data, indent=2)}]})
            results.append({'request': name, 'method': method, 'path': path, 'status': status, 'passed': True})
            return data
        try:
            created = record('1. Add user', 'POST', '/api/users/add', user,
                             lambda d: d['name'] == user['name'] and type(d['user_id']) is int)
            uid = created['user_id']
            record('2. Get all users', 'GET', '/api/users', check=lambda d: d == [created])
            record('3. Get user by ID', 'GET', f'/api/users/{uid}', check=lambda d: d == created)
            updated = dict(user, user_id=uid, name='Jane Doe', email='janedoe@example.com')
            record('4. Update user', 'PUT', '/api/users/update', updated, lambda d: d == updated)
            assert send('GET', f'/api/users/{uid}') == (200, updated)
            patched = dict(updated, country='Lebanon')
            record('5. Patch user', 'PATCH', f'/api/users/{uid}', {'country': 'Lebanon'}, lambda d: d == patched)
            assert send('GET', f'/api/users/{uid}') == (200, patched)
            record('6. Delete user', 'DELETE', f'/api/users/delete/{uid}',
                   check=lambda d: d['status'] == 'User deleted successfully')
            assert send('GET', '/api/users') == (200, [])
            for method, path, body, expected in [
                ('GET', f'/api/users/{uid}', None, 404),
                ('DELETE', f'/api/users/delete/{uid}', None, 404),
                ('PUT', '/api/users/update', updated, 404),
                ('PATCH', f'/api/users/{uid}', {'country': 'Lebanon'}, 404),
                ('PATCH', f'/api/users/{uid}', {}, 400),
                ('PATCH', f'/api/users/{uid}', {'user_id': 99}, 400),
                ('PATCH', f'/api/users/{uid}', {'country': ''}, 400),
                ('POST', '/api/users/add', {}, 400),
                ('POST', '/api/users/add', [], 400),
                ('PUT', '/api/users/update', dict(user, user_id='bad'), 400),
                ('POST', '/api/users/add', dict(user, name=' '), 400)]:
                status, data = send(method, path, body)
                assert status == expected and 'error' in data
                results.append({'method': method, 'path': path, 'status': status, 'passed': True})
            for item in items:
                req = item['request']
                if req['method'] in ('PATCH', 'DELETE') or item['name'].startswith('3.'):
                    req['url']['raw'] = req['url']['raw'].rsplit('/', 1)[0] + '/{{user_id}}'
                    req['url']['path'][-1] = '{{user_id}}'
                if req['method'] == 'PUT':
                    req['body']['raw'] = req['body']['raw'].replace('"user_id": ' + str(uid), '"user_id": {{user_id}}')
            out = Path('postman')
            out.mkdir(exist_ok=True)
            collection = {'info': {'name': 'Flask user app',
                'description': 'Lab 5 CRUD requests. Select the Lab5 Local environment and run in numbered order. Examples captured from real HTTP responses against an isolated SQLite database.',
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'}, 'item': items}
            environment = {'name': 'Lab5 Local', 'values': [
                {'key': 'base_url', 'value': 'http://localhost:5000', 'type': 'default', 'enabled': True}],
                '_postman_variable_scope': 'environment'}
            (out / 'Flask user app.postman_collection.json').write_text(json.dumps(collection, indent=2), encoding='utf-8')
            (out / 'Lab5 Local.postman_environment.json').write_text(json.dumps(environment, indent=2), encoding='utf-8')
            Path('verification.json').write_text(json.dumps({'transport': 'real local HTTP', 'database': 'isolated temporary SQLite', 'results': results,
                'additional_checks': ['updated data persisted', 'deleted user absent from list']}, indent=2), encoding='utf-8')
            print(f'PASS: {len(results)} HTTP scenarios plus persistence/deletion checks; Postman exports generated.')
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

if __name__ == '__main__':
    main()
