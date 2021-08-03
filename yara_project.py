import time
import sys
import requests
import csv
import argparse


class GitReport:
    def __init__(self, organisation, client):
        self.org = organisation
        self.client = client
        self.info = {}
        self.remaining_rate_limit = 5000
        self.rate_limit_sleep_time = 4000

    def get_api_response(self, url):
        try:
            if self.remaining_rate_limit < 5:
                print('Rate limit exceeded. Hence sleeping for 1 hour.')
                time.sleep(self.rate_limit_sleep_time)
            if 'per_page' not in url:
                url = url + '?per_page=100'
            resp = self.client.get(url)
            self.remaining_rate_limit = int(resp.headers.get('X-RateLimit-Remaining', self.remaining_rate_limit))
            next_page = ''
            if 'next' in resp.links.keys():
                next_page = resp.links['next']['url']
            return resp.json(), next_page
        except Exception as err:
            print(err)
            return '', ''

    def get_repo_url(self):
        url = 'https://api.github.com/orgs/{}/repos'.format(self.org)
        return url

    def get_email_name(self, repo_name, login):
        try:
            if self.remaining_rate_limit < 5:
                print('Rate limit exceeded. Hence sleeping for 1 hour.')
                time.sleep(self.rate_limit_sleep_time)
            url = 'https://api.github.com/repos/{}/{}/commits?author={}'.format(self.org, repo_name, login)
            resp = self.client.get(url)
            self.remaining_rate_limit = int(resp.headers.get('X-RateLimit-Remaining', self.remaining_rate_limit))
            resp = resp.json()
            name = resp[0]['commit']['author']['name']
            email = resp[0]['commit']['author']['email']
            return name, email
        except Exception as err:
            print(err)
            return '', ''

    def get_git_report(self):
        try:
            repo_url = self.get_repo_url()
            while repo_url:
                repo_resp = self.get_api_response(repo_url)
                repo_url = repo_resp[1]
                repo_list = repo_resp[0]

                for repo in repo_list:
                    repo_name = repo.get('name')

                    languages_url = repo.get('languages_url')
                    languages = []
                    while languages_url:
                        languages_resp = self.get_api_response(languages_url)
                        languages_url = languages_resp[1]
                        languages.extend(list(languages_resp[0].keys()))

                    contributors_url = repo.get('contributors_url')
                    while contributors_url:
                        contributors_resp = self.get_api_response(contributors_url)
                        contributors_url = contributors_resp[1]
                        contributors_list = contributors_resp[0]

                        for contributor in contributors_list:
                            login = contributor.get('login')
                            if login in self.info:
                                self.info[login]['repositories'].append(repo_name)
                                for language in languages:
                                    if language not in self.info[login]['languages']:
                                        self.info[login]['languages'].append(language)
                            else:
                                name, email = self.get_email_name(repo_name, login)
                                self.info[login] = {'login': login, 'name': name, 'email': email,
                                                    'repositories': [repo_name], 'languages': languages}

            for i in self.info.values():
                i['repositories'] = ", ".join(i['repositories'])
                i['languages'] = ", ".join(i['languages'])

            fields = ['login', 'name', 'email', 'repositories', 'languages']

            with open('yara.csv', 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=';')
                writer.writeheader()
                writer.writerows(self.info.values())
        except Exception as err:
            print(err)


if __name__ == '__main__':
    try:

        parser = argparse.ArgumentParser()
        parser.add_argument("--organisation", type=str, required=True)
        parser.add_argument("--personal_access_token", type=str, required=True)
        args = parser.parse_args()
        organisation = args.organisation
        access_token = args.personal_access_token

        client = requests.session()
        headers = {"Authorization": "token {}".format(access_token)}
        client.headers.update(headers)

        gitreport = GitReport(organisation, client)
        gitreport.get_git_report()

    except Exception as err:
        print('Error: {}'.format(err))
        sys.exit(0)