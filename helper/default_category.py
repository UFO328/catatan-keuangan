from transaction.models import Category


DEFAULT_CATEGORIES = [
    "Makan",
    "Transportasi",
    "Belanja",
    "Tagihan",
    "Hiburan",
    "Uang Saku",
    "Lainnya",
]


def create_default_categories(user):
    categories = [
        Category(
            user=user,
            name=name,
            is_default=True,
        )
        for name in DEFAULT_CATEGORIES
    ]

    Category.objects.bulk_create(categories)