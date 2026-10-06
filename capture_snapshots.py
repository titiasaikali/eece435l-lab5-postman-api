"""Capture browser screenshots of live API requests, using an isolated DB."""
import json
import os
import tempfile
import threading
from pathlib import Path

def main():
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as temp:
        os.environ['LAB5_DATABASE'] = str(Path(temp) / 'evidence.db')
        from app import app
        from flask import send_file
        from werkzeug.serving import make_server
        @app.get('/lab-evidence')
        def evidence_page():
            return send_file(Path(__file__).parent / 'evidence' / 'api-client.html')
        server = make_server('127.0.0.1', 5000, app)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        out=Path('snapshots')
        out.mkdir(exist_ok=True)
        records=[]
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(channel='msedge', headless=True)
                page=browser.new_page(viewport={'width':1440,'height':960}, device_scale_factor=1)
                page.goto('http://localhost:5000/lab-evidence')
                user=dict(name='John Doe',email='johndoe@example.com',phone='067765434567',
                          address='John Doe Street, Innsbruck',country='Austria')
                def capture(filename,title,method,path,body=None,expected=200):
                    page.locator('#case').evaluate('(el, text) => el.textContent = text', title)
                    page.locator('#method').select_option(method)
                    page.locator('#url').fill('http://localhost:5000'+path)
                    page.locator('#body').fill(json.dumps(body,indent=2) if body is not None else '')
                    page.evaluate('window.finished = false')
                    page.locator('#send').click()
                    page.wait_for_function('window.finished === true')
                    result=page.evaluate('window.lastResponse')
                    assert result.get('status')==expected, result
                    page.screenshot(path=str(out/filename),full_page=True)
                    records.append(dict(screenshot=filename,method=method,url='http://localhost:5000'+path,
                                        request_body=body,response=result))
                    return result['body']
                capture('01-get-empty.png','1. GET — initial database is empty','GET','/api/users')
                created=capture('02-post-create.png','2. POST — create a user','POST','/api/users/add',user)
                uid=created['user_id']
                assert created['name']==user['name']
                listed=capture('03-get-list.png','3. GET — retrieve the user list','GET','/api/users')
                assert listed==[created]
                assert capture('04-get-user.png','4. GET — retrieve one user','GET',f'/api/users/{uid}')==created
                updated=dict(user,user_id=uid,name='Jane Doe',email='janedoe@example.com')
                assert capture('05-put-update.png','5. PUT — replace the user fields','PUT','/api/users/update',updated)==updated
                patched=dict(updated,country='Lebanon')
                assert capture('06-patch-update.png','6. PATCH — change country and preserve other fields','PATCH',f'/api/users/{uid}',{'country':'Lebanon'})==patched
                assert capture('07-get-after-update.png','7. GET — verify persisted PUT and PATCH changes','GET',f'/api/users/{uid}')==patched
                capture('08-delete-user.png','8. DELETE — remove the user','DELETE',f'/api/users/delete/{uid}')
                assert capture('09-get-after-delete.png','9. GET — verify that the user was deleted','GET','/api/users')==[]
                capture('10-get-not-found.png','10. GET — deleted user returns HTTP 404','GET',f'/api/users/{uid}',expected=404)
                browser.close()
            (out/'requests-and-results.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
            print('PASS: 10 live browser request screenshots captured, including POST, GET, PUT, PATCH and DELETE.')
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

if __name__=='__main__':
    main()
