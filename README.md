# yara_project

Prerequisites: Python 3.x

Clone the repository:

git clone https://github.com/sumertulsyan-per/yara_project.git

Script Name: yara_project.py

Objective:

This script takes organisation name and personal access token of the user's github account.
It fetches all the repositories from the given organisation and all the languages used and all the contributors who have pused the codeto the given repository.
One thing to note is that script will sleep will for 1 hour and resume the flow in case rate limit exceeds the permissible limit. (5000 for authenticated request usually).

Output:

Final Output will be csv file 'yara.csv' with all the required information. The csv file will be in same directory from where the script has been executed.

Execution command:

python yara_project.py --organisation <organisation_name> --personal_access_token <personal_access_token>

For Example: python yara_project.py --organisation potato --personal_access_token 123458fffft5555

Note:

The scipt will run on Python 3.x only.

personal_access_token for any github user account can be created by follwing this link https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token
