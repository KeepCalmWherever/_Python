import requests
import sys
from pytest_httpserver import HTTPServer

def gather_issues_list(Command = "local_test", Org="devopshq", Token="<your_token>", Accept="application/json", Environment="http://localhost:4000"):
  if Environment == "http://localhost:4000" and Command == "local_test":
    server = HTTPServer(port=4000)
    server.expect_request("/orgs/devopshq/repos").respond_with_json([{"name": "crosspm"}, {"name": "vspheretools"}, {"name": "FuzzyClassificator"}])
    server.expect_request("/repos/devopshq/FuzzyClassificator/issues").respond_with_json([])
    server.expect_request("/repos/devopshq/crosspm/issues").respond_with_json([{"created_at": "2018-04-24T10:33:17Z", "number": "1232232", "title": "internal check1", "html_url": "http://test_url_crosspm1"}, {"created_at": "2018-04-22T10:33:17Z", "number": "331265", "title": "internal check2", "html_url": "http://test_url_crosspm2"}])
    server.expect_request("/repos/devopshq/vspheretools/issues").respond_with_json([{"created_at": "2018-04-24T10:33:17Z", "number": "123232133", "title": "internal check1", "html_url": "http://test_url_vspheretools1"}, {"created_at": "2018-04-22T10:33:17Z", "number": "3312", "title": "internal check2", "html_url": "http://test_url_vspheretools2"}])
    server.start()
    ReposPerOrg = (requests.get(f'{Environment}/orgs/{Org}/repos', headers={'Accept': f'{Accept}', 'Authorization': f'Bearer {Token}'})).json()
    for Repo in ReposPerOrg:
      RepoName = Repo['name']
      Issues = (requests.get(f'{Environment}/repos/{Org}/{RepoName}/issues', headers={'Accept': f'{Accept}', 'Authorization': f'Bearer {Token}'})).json()
      if len(Issues) == 0:
        print(RepoName + ":", 'no issues existing', sep='\n')
        print('\n')
      else:
        print(RepoName + ":", sep='\n')
        for Issue in Issues:
          print((str(Issue['created_at'])).strip()  + " " + "#" + (str(Issue['number'])).strip() + " " + str(Issue['title'] + " " + (str(Issue['html_url'])).strip()))
      print(sep='\n\n')
    server.stop()
  elif Environment == "https://api.github.com" and Command == "--get-all-issues":
    ReposPerOrg = (requests.get(f'{Environment}/orgs/{Org}/repos', headers={'Accept': f'{Accept}', 'Authorization': f'Bearer {Token}'})).json()
    for Repo in ReposPerOrg:
      RepoName = Repo['name']
      Issues = (requests.get(f'{Environment}/repos/{Org}/{RepoName}/issues', headers={'Accept': f'{Accept}', 'Authorization': f'Bearer {Token}'})).json()
      if len(Issues) == 0:
        print(RepoName + ":", 'no issues existing', sep='\n')
      else:
        print(RepoName + ":", sep='\n')
        for Issue in Issues:
          print((str(Issue['created_at'])).strip() + " " + "#" + (str(Issue['number'])).strip() + " " + str(Issue['title'] + " " + (str(Issue['html_url'])).strip()))
      print(sep='\n\n')
  elif Environment == "https://api.github.com" and Command == "--help":
    print("Supported commands:")
    print("--get-all-issues - to collect all issues from devopshq github project")
  else:
    print("Failed: unknowned command passed, use --help to check options")

if __name__ == "__main__":
  EnvironmentPassed = str(sys.argv[1])
  CommandPassed = str(sys.argv[2])
  gather_issues_list(Environment=EnvironmentPassed,Command = CommandPassed)
