import requests

class UpdateChecker:
    def __init__(self, repository, current_version):
        self.repository = repository
        self.current_version = current_version

    def check_for_update(self):
        # GitHub API URL for the releases
        api_url = f'https://api.github.com/repos/{self.repository}/releases/latest'
        response = requests.get(api_url)

        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name']
            return self.compare_versions(latest_version)
        else:
            print("Error fetching releases from GitHub.")
            return False

    def compare_versions(self, latest_version):
        if self.current_version < latest_version:
            print(f'New version available: {latest_version}')
            return True
        else:
            print('You are using the latest version.')
            return False

# Example usage:
if __name__ == '__main__':
    checker = UpdateChecker('owner/repository', '1.0.0')  # replace with actual repository
    checker.check_for_update()