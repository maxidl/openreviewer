import openreview


def get_client(version, or_username, or_password):
    if version == 1:
        print("creating v1 client")
        return openreview.Client(
            username=or_username,
            password=or_password,
            baseurl="https://api.openreview.net",
        )
    elif version == 2:
        print("creating v2 client")
        return openreview.api.OpenReviewClient(
            username=or_username,
            password=or_password,
            baseurl="https://api2.openreview.net",
        )
    else:
        raise ValueError(
            "version must be in {1,2}, but specified version is: " + version
        )
