from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def login(self):
        self.client.get("/")

    @task
    def signup(self):
        self.client.get("/signup/")

    @task
    def home(self):
        self.client.get("/home/")

    @task
    def upload(self):
        self.client.get("/upload/")

    @task
    def dashboard(self):
        self.client.get("/dashboard/")

    @task
    def help(self):
        self.client.get("/help/")

    @task
    def download_template(self):
        self.client.get("/temp/download")

    @task
    def download_invalid_excel(self):
        self.client.get("/download-invalid-excel/")

    @task
    def error_page(self):
        self.client.get("/error_data_page")

    @task
    def password_reset(self):
        self.client.get("/password_reset")

    @task
    def password_reset_done(self):
        self.client.get("/password_reset_done/")

    @task
    def password_change_done(self):
        self.client.get("/password_change/done/")