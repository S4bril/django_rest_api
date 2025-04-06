class DatasetManager():

    def load(self):
        with open("SocialMediaUsersDataset.csv", "r") as file:
            for line in file:
                print(line)


if __name__ == "__main__":
    manager = DatasetManager()
    manager.load()
