from reactk.model2.ants.key_accessor import KeyAccessor
from reactk.model2.prop_model.prop import Prop_Mapping, Prop_Schema


class PropValuesAccessor(KeyAccessor[Prop_Mapping]):
    @property
    def key(self) -> str:
        return "__PROP_VALUES__"


class PropsAccessor(KeyAccessor[Prop_Schema]):
    @property
    def key(self) -> str:
        return "__PROPS__"
