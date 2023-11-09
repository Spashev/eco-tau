def update_instance(instance, data) -> None:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()
