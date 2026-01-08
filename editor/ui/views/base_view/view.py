class BaseView:
    def __init__(self, editor):
        self.editor = editor
        self.model = None
    
    def set_model(self, model):
        self.cleanup()
        self.model = model
        if self.model is not None:
            self.model.deleted.connect(self.on_model_deleted)
            self.display()
        else:
            self.display_empty()

    def on_model_deleted(self):
        self.set_model(None)

    def display(self): # For displaying a model
        pass

    def display_empty(self): # For displaying when there is no model
        pass

    def cleanup(self): # For cleaning up previous model when displaying a new one
        if self.model is not None:
            self.model.deleted.disconnect(self.on_model_deleted)
