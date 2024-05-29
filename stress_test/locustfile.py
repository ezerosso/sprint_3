from locust import HttpUser, between, task, TaskSet

class UserBehavior(TaskSet):
    @task
    def index(self):
        self.client.get("/")

    @task
    def predict(self):
        # Ajusta la ruta al archivo de imagen que quieres enviar en la solicitud
        image_path = '/home/ezequiel/Descargas/assignment/assignment/stress_test/dog.jpeg'
        with open(image_path, 'rb') as image_file:
            files = {'file': image_file}
            self.client.post("/predict", files=files)

class APIUser(HttpUser):
    wait_time = between(1, 5)

    # Put your stress tests here.
    # See https://docs.locust.io/en/stable/writing-a-locustfile.html for help.
    # TODO
    tasks = [UserBehavior]
    wait_time = between(1, 5)
