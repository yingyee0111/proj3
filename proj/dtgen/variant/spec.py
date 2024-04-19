from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    FrozenSet,
    Optional,
    Sequence,
    Any,
    Mapping,
)
from proj.dtgen.render_utils import (
    IncludeSpec,
    parse_include_spec,
)
import proj.toml as toml
from pathlib import Path

class Feature(Enum):
    EQ = auto()
    ORD = auto()
    HASH = auto()
    JSON = auto()
    # FMT = auto()
    # RAPIDCHECK = auto()

@dataclass(frozen=True)
class ValueSpec:
    type_: str
    _json_key: Optional[str]

    @property
    def json_key(self) -> str:
        if self._json_key is None:
            return self.type_
        else:
            return self._json_key

@dataclass(frozen=True)
class VariantSpec:
    includes: Sequence[IncludeSpec]
    namespace: Optional[str]
    name: str
    values: Sequence[ValueSpec]
    features: FrozenSet[Feature]

def parse_feature(raw: str) -> Feature:
    if raw == 'eq':
        return Feature.EQ
    elif raw == 'ord':
        return Feature.ORD
    elif raw == 'hash':
        return Feature.HASH
    elif raw == 'json':
        return Feature.JSON
    else:
        raise ValueError(f'Unknown feature: {raw}')

def parse_value_spec(raw: Mapping[str, Any]) -> ValueSpec:
    return ValueSpec(
        type_=raw['type'],
        _json_key=raw.get('json_key', None),
    )

def parse_variant_spec(raw: Mapping[str, Any]) -> VariantSpec:
    return VariantSpec(
        namespace=raw.get('namespace', None),
        includes=[parse_include_spec(include) for include in raw.get('includes', [])],
        name=raw['name'],
        values=[parse_value_spec(value) for value in raw['values']],
        features=frozenset([parse_feature(feature) for feature in raw['features']]),
    )

def load_spec(path: Path) -> VariantSpec:
    try:
        with path.open('r') as f:
            raw = toml.loads(f.read())
    except toml.TOMLDecodeError as e:
        raise RuntimeError(f'Failed to load spec {path}') from e
    try:
        return parse_variant_spec(raw)
    except KeyError as e:
        raise RuntimeError(f'Failed to parse spec {path}') from e