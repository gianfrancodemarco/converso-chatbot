from typing import Literal, Optional, Type, Any

from pydantic import BaseModel, Field, field_validator, model_validator

from converso.conversational_engine.form_agent import FormTool


class OnlinePurchasePayload(BaseModel):

    allowed_provinces_: list = []

    item: Literal["watch", "shoes", "phone", "book"] = Field(
        description="Item to purchase"
    )

    ebook: Optional[bool] = Field(
        description="If true, the book will be sent as an ebook, if false it will be sent as a physical copy. Required if item is book"
    )

    email: Optional[str] = Field(
        description="Email to send the ebook to"
    )

    quantity: int = Field(
        description="Quantity of items to purchase, between 1 and 10"
    )

    region: str = Field(
        description="Region to ship the item"
    )

    province: Optional[str] = Field(
        description="Province to ship the item"
    )

    address: str = Field(
        description="Address to ship the item to"
    )

    @field_validator("quantity")
    def validate_quantity(cls, v):
        if v is not None:
            if v < 1 or v > 10:
                raise ValueError("Quantity must be between 1 and 10")
        return v

    @field_validator("region")
    def validate_region(cls, v):
        if v is not None:
            if v not in ["puglia", "sicilia", "toscana"]:
                raise ValueError(
                    "Region must be one of puglia, sicilia, toscana")
        return v

    @model_validator(mode="before")
    def set_allowed_provinces(cls, values: Any) -> Any:
        region = values.get("region").lower() if values.get("region") else None
        province = values.get("province").lower(
        ) if values.get("province") else None

        if region:
            allowed_provinces = []
            if region == "puglia":
                allowed_provinces = ["bari", "bat",
                                     "brindisi", "foggia", "lecce", "taranto"]
            if region == "sicilia":
                allowed_provinces = ["agrigento", "caltanissetta", "catania",
                                     "enna", "messina", "palermo", "ragusa", "siracusa", "trapani"]
            if region == "toscana":
                allowed_provinces = ["arezzo", "firenze", "grosseto", "livorno",
                                     "lucca", "massa-carrara", "pisa", "pistoia", "prato", "siena"]
            values.update({
                "region": region,
                "province": province,
                "allowed_provinces_": allowed_provinces
            })
        return values

    @model_validator(mode="before")
    def validate_ebook(cls, values: Any) -> Any:
        if values.get("item") == "book" and values.get("ebook") is None:
            raise ValueError("Ebook must be set for books")
        return values

    @model_validator(mode="after")
    def validate_province(cls, model: "OnlinePurchasePayload"):
        if model.region and model.province:
            if model.province not in model.allowed_provinces_:
                raise ValueError(f"""Province must be one of {
                                 model.allowed_provinces_}""")
        return model


class OnlinePurchase(FormTool):
    name = "OnlinePurchase"
    description = """Purchase an item from an online store"""
    args_schema: Type[BaseModel] = OnlinePurchasePayload

    def _run_when_complete(
        self,
        *args,
        **kwargs
    ) -> str:
        return "OK"

    def get_next_field_to_collect(
        self,
        **kwargs
    ) -> str:
        """
        The default implementation returns the first field that is not set.
        """
        if not self.form.item:
            return "item"

        if self.form.item == "book":
            if self.form.ebook == None:
                return "ebook"
            if self.form.ebook == True:
                if not self.form.email:
                    return "email"
                else:
                    return None

        if not self.form.quantity:
            return "quantity"

        if not self.form.region:
            return "region"

        if not self.form.province:
            return "province"

        if not self.form.address:
            return "address"

        return None
