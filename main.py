def main():
    print("Hello from doccompanion!")


if __name__ == "__main__":
    main()

'''
Anywhere in app

from apps.settings.services import SettingsService

settings = SettingsService.get()

chunk_size = settings.chunk_size
'''