from ..base_model import BaseModel
from editor.ui.views.properties.view import PropertyView


class PropertiesModel(BaseModel):
    recommended_view = PropertyView
    def __init__(self):
        super().__init__()
        self.properties = self.default_properties

    @property
    def default_properties(self):
        return {}
    
    def cleanup(self):
        for prop in self.properties.values():
            prop.cleanup()
        super().cleanup()
