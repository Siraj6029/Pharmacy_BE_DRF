class ProductTypeChoices:
    TAB = "TAB", "Tablets"
    SYP = "SYP", "Syrup"
    CR = "CR", "Cream"
    CAP = "CAP", "Capsule"
    INJ = "INJ", "Injection"
    DRO = "DRO", "Drops"
    DRI = "DRI", "Drips"
    SEC = "SEC", "Sechet"
    OTH = "OTH", "Others"

    @classmethod
    def get_choices(cls):
        return (
            cls.TAB,
            cls.SYP,
            cls.CR,
            cls.CAP,
            cls.INJ,
            cls.DRO,
            cls.DRI,
            cls.SEC,
            cls.OTH,
        )
