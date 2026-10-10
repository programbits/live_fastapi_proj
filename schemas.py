from pydantic import BaseModel, ConfigDict, Field, field_validator


class BlogCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=100_000)

    @field_validator("title", "content")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class BlogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str


class BlogListResponse(BaseModel):
    page: int
    limit: int
    total: int
    data: list[BlogResponse]
