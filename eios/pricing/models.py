"""Physical C1 contracts for EIOS Price Intelligence."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from .representativeness import RepresentativenessObservation
from .sufficiency import SufficiencyObservation
ComparabilityStatus=Literal["COMPARABLE","NO_COMPARABLE","PENDING"]
NormalizationStatus=Literal["NORMALIZED","PENDING","NOT_NORMALIZABLE"]
TemporalStatus=Literal["ELIGIBLE","INELIGIBLE","INDETERMINATE"]
RepresentativenessStatus=Literal["REPRESENTATIVE","NON_REPRESENTATIVE","INDETERMINATE"]
SufficiencyStatus=Literal["SUFFICIENT","LIMITED","NOT_JUSTIFIABLE"]
PRStatus=Literal["PR_AVAILABLE","PR_LIMITED","PR_NOT_JUSTIFIABLE"]
AggregationMethod=Literal["MEDIAN_UNWEIGHTED"]
EconomicBasisStatus=Literal["RESOLVED","NOT_APPLICABLE","PENDING","NOT_RESOLVABLE"]
EconomicDimension=Literal["UNIT","QUANTITY","CURRENCY","TAX","TRANSPORT","DISCOUNT","SURCHARGE","COMMERCIAL"]
class PriceReference(BaseModel):
    model_config=ConfigDict(extra="forbid",str_strip_whitespace=True)
    source_transaction_id:str=Field(min_length=1,max_length=128);article_identity:str=Field(min_length=1,max_length=128);supplier_identity:str|None=Field(default=None,max_length=128);quantity:Decimal=Field(gt=0);unit:str=Field(min_length=1,max_length=32);unit_price:Decimal=Field(ge=0,decimal_places=4);currency:str=Field(min_length=3,max_length=3);operation_date:date;commercial_conditions:str|None=Field(default=None,max_length=512);evidence_refs:tuple[str,...]=()
    @model_validator(mode="after")
    def finite_values(self)->"PriceReference":
        if not self.unit_price.is_finite() or not self.quantity.is_finite():raise ValueError("Los valores de precio y cantidad deben ser finitos")
        return self
class NormalizationBasis(BaseModel):
    model_config=ConfigDict(extra="forbid",str_strip_whitespace=True,frozen=True)
    target_unit:str=Field(min_length=1,max_length=32);target_tax_basis:str|None=Field(default=None,max_length=64);target_transport_basis:str|None=Field(default=None,max_length=64);target_discount_basis:str|None=Field(default=None,max_length=64);target_surcharge_basis:str|None=Field(default=None,max_length=64);target_commercial_basis:str|None=Field(default=None,max_length=128);basis_reference:str=Field(min_length=1,max_length=256);rule_reference:str=Field(min_length=1,max_length=128);trace_reference:str=Field(min_length=1,max_length=128)
class EconomicBasisEvidence(BaseModel):
    model_config=ConfigDict(extra="forbid",frozen=True)
    reference_id:str=Field(min_length=1,max_length=128);dimension:EconomicDimension;status:EconomicBasisStatus;evidence_refs:tuple[str,...]=();rule_reference:str|None=None;trace_reference:str|None=None;justification:str|None=None
    @model_validator(mode="after")
    def trace_requirements(self)->"EconomicBasisEvidence":
        if self.status in {"RESOLVED","NOT_APPLICABLE"} and (not self.evidence_refs or not self.rule_reference or not self.trace_reference):raise ValueError("RESOLVED/NOT_APPLICABLE requieren evidencia, regla y traza")
        if self.status in {"PENDING","NOT_RESOLVABLE"} and not self.justification:raise ValueError("PENDING/NOT_RESOLVABLE requieren justificación")
        return self
class EconomicBasisAssessment(BaseModel):
    model_config=ConfigDict(extra="forbid",frozen=True)
    records:tuple[EconomicBasisEvidence,...]=()
    @property
    def all_resolved(self)->bool:
        if not self.records:return False
        dimensions=[r.dimension for r in self.records]
        return len(dimensions)==len(set(dimensions)) and all(r.status in {"RESOLVED","NOT_APPLICABLE"} for r in self.records)
class NormalizationRecord(BaseModel):
    model_config=ConfigDict(extra="forbid")
    field:str=Field(min_length=1,max_length=64);original_value:str;normalized_value:str;rule_reference:str=Field(min_length=1,max_length=128);trace_reference:str=Field(min_length=1,max_length=128)
class PriceConversionInstruction(BaseModel):
    """Explicit price multiplication: target price = source price * factor.

    This contract records a proposed conversion and its documentary links.
    External source authentication remains the responsibility of intake/QTG.
    For UNIT, factor is target-price-per-unit / source-price-per-unit.
    For CURRENCY, factor is target-currency per one source-currency.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
    reference_id: str = Field(min_length=1, max_length=128)
    dimension: Literal["UNIT", "CURRENCY"]
    source_code: str = Field(min_length=1, max_length=32)
    target_code: str = Field(min_length=1, max_length=32)
    factor: Decimal = Field(gt=0, max_digits=22, decimal_places=16)
    effective_date: date
    source_ref: str = Field(min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = Field(min_length=1)
    rule_reference: str = Field(min_length=1, max_length=128)
    trace_reference: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def check_conversion(self) -> "PriceConversionInstruction":
        if self.source_code == self.target_code:
            raise ValueError("La conversión exige códigos de origen y destino distintos")
        if not self.factor.is_finite():
            raise ValueError("El factor de conversión debe ser finito")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("La conversión tiene evidencias duplicadas")
        if any(not value.strip() for value in self.evidence_refs):
            raise ValueError("La conversión requiere referencias de evidencia no vacías")
        return self


class PriceEconomicBasisComparison(BaseModel):
    """Source-bound equivalence check for economic price bases.

    This is NOT an instruction to adjust a price numerically. Evidence
    provenance/authority must be validated by the invoking intake pipeline.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
    reference_id: str = Field(min_length=1, max_length=128)
    dimension: Literal["QUANTITY", "TAX", "TRANSPORT", "DISCOUNT", "SURCHARGE", "COMMERCIAL"]
    source_basis: str = Field(min_length=1, max_length=256)
    target_basis: str = Field(min_length=1, max_length=256)
    status: Literal["EQUIVALENT", "NOT_APPLICABLE", "DIFFERENT", "INDETERMINATE"]
    source_ref: str = Field(min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = Field(min_length=1)
    rule_reference: str = Field(min_length=1, max_length=128)
    trace_reference: str = Field(min_length=1, max_length=128)
    justification: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def validate_comparison(self) -> "PriceEconomicBasisComparison":
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("Evidencias duplicadas en comparación de base económica")
        if any(not item.strip() for item in self.evidence_refs):
            raise ValueError("Las evidencias de base económica no pueden estar vacías")
        if self.status in {"DIFFERENT", "INDETERMINATE"} and not self.justification:
            raise ValueError("Una base no equivalente o indeterminada requiere justificación")
        if self.status == "EQUIVALENT" and self.dimension != "QUANTITY" and self.source_basis != self.target_basis:
            raise ValueError("Bases económicas distintas no pueden declararse equivalentes sin una transformación")
        if self.status == "EQUIVALENT" and self.dimension == "QUANTITY" and self.source_basis != self.target_basis and not self.justification:
            raise ValueError("La equivalencia entre cantidades diferentes requiere justificación")
        return self


class PriceReferenceAssessment(BaseModel):
    model_config=ConfigDict(extra="forbid")
    reference_id:str=Field(min_length=1,max_length=128);comparability:ComparabilityStatus;normalization_status:NormalizationStatus="PENDING";temporal_status:TemporalStatus="INDETERMINATE";temporal_rule_reference:str|None=None;representativeness:RepresentativenessStatus="INDETERMINATE";normalized_unit_price:Decimal|None=Field(default=None,ge=0,decimal_places=4);normalization:tuple[NormalizationRecord,...]=();economic_basis:EconomicBasisAssessment|None=None;limitation_refs:tuple[str,...]=()
    @model_validator(mode="after")
    def normalization_value_matches_status(self)->"PriceReferenceAssessment":
        if self.normalization_status=="NORMALIZED" and self.normalized_unit_price is None:raise ValueError("NORMALIZED requiere normalized_unit_price")
        if self.normalization_status!="NORMALIZED" and self.normalized_unit_price is not None:raise ValueError("Una referencia no normalizada no puede tener normalized_unit_price")
        return self
class PriceIntelligenceInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    decision_context:DecisionContext;purchase_operation:PurchaseOperation;references:tuple[PriceReference,...]=();evidence_validations:tuple[EvidenceValidation,...]=();normalization_basis:NormalizationBasis|None=None;economic_basis_evidence:tuple[EconomicBasisEvidence,...]=();price_conversion_instructions:tuple[PriceConversionInstruction,...]=();economic_basis_comparisons:tuple[PriceEconomicBasisComparison,...]=();methodology_version:str=Field(min_length=1,max_length=64)
    @model_validator(mode="after")
    def context_matches_purchase(self)->"PriceIntelligenceInput":
        if self.decision_context.decision_id!=self.purchase_operation.decision_id:raise ValueError("decision_id no coincide entre contexto y operación")
        if self.decision_context.scenario_id!=self.purchase_operation.scenario_id:raise ValueError("scenario_id no coincide entre contexto y operación")
        return self
    @model_validator(mode="after")
    def evidence_refs_are_known(self)->"PriceIntelligenceInput":
        known={x.evidence_id for x in self.evidence_validations};referenced={r for item in self.references for r in item.evidence_refs};unknown=referenced-known
        if unknown:raise ValueError("Existen evidence_refs sin EvidenceValidation correspondiente")
        economic_refs={e for item in self.economic_basis_evidence for e in item.evidence_refs};unknown_economic=economic_refs-known
        if unknown_economic:raise ValueError("Existen economic evidence_refs sin EvidenceValidation correspondiente")
        reference_ids={r.source_transaction_id for r in self.references};unknown_references={e.reference_id for e in self.economic_basis_evidence}-reference_ids
        if unknown_references:raise ValueError("EconomicBasisEvidence referencia una PriceReference inexistente")
        conversions=self.price_conversion_instructions
        if len({(c.reference_id,c.dimension) for c in conversions})!=len(conversions):
            raise ValueError("Conversiones duplicadas por referencia y dimensión")
        if {c.reference_id for c in conversions}-reference_ids:
            raise ValueError("Una conversión referencia una PriceReference inexistente")
        if {e for c in conversions for e in c.evidence_refs}-known:
            raise ValueError("Una conversión referencia evidencia desconocida")
        comparisons=self.economic_basis_comparisons
        if len({(c.reference_id,c.dimension) for c in comparisons}) != len(comparisons):
            raise ValueError("Comparaciones económicas duplicadas por referencia y dimensión")
        if {c.reference_id for c in comparisons}-reference_ids:
            raise ValueError("Una comparación económica referencia una PriceReference inexistente")
        if {e for c in comparisons for e in c.evidence_refs}-known:
            raise ValueError("Una comparación económica referencia evidencia desconocida")
        return self
class PriceIntelligenceAssessmentContext(BaseModel):
    model_config=ConfigDict(extra="forbid",frozen=True)
    temporal:dict[str,tuple[TemporalStatus,str|None]]=Field(default_factory=dict)
    representativeness:dict[str,RepresentativenessObservation]=Field(default_factory=dict)
    sufficiency:SufficiencyObservation
class PriceCounts(BaseModel):
    model_config=ConfigDict(extra="forbid",frozen=True)
    n_raw:int=Field(ge=0);n_unique:int=Field(ge=0);n_comparable:int=Field(ge=0);n_representative:int=Field(ge=0);n_selected:int=Field(ge=0)
    @model_validator(mode="after")
    def monotonic_counts(self)->"PriceCounts":
        values=(self.n_raw,self.n_unique,self.n_comparable,self.n_representative,self.n_selected)
        if any(a<b for a,b in zip(values,values[1:])):raise ValueError("Los conteos C1 deben ser monótonos no crecientes")
        return self
class PriceIntelligenceResult(BaseModel):
    model_config=ConfigDict(extra="forbid",frozen=True)
    decision_id:str;scenario_id:str;data_snapshot_id:str;methodology_version:str;pr_value:Decimal|None=Field(default=None,ge=0,decimal_places=4);currency:str|None=Field(default=None,min_length=3,max_length=3);sufficiency_status:SufficiencyStatus;pr_status:PRStatus;pr_limitations:tuple[str,...]=();reference_set:tuple[str,...]=();counts:PriceCounts;aggregation_method:AggregationMethod;trace_references:tuple[str,...]=()
    @model_validator(mode="after")
    def enforce_result_invariants(self)->"PriceIntelligenceResult":
        expected={"SUFFICIENT":"PR_AVAILABLE","LIMITED":"PR_LIMITED","NOT_JUSTIFIABLE":"PR_NOT_JUSTIFIABLE"}[self.sufficiency_status]
        if self.pr_status!=expected:raise ValueError("pr_status no coincide con sufficiency_status")
        if self.pr_status in {"PR_AVAILABLE","PR_LIMITED"} and self.pr_value is None:raise ValueError("PR_AVAILABLE/PR_LIMITED requieren pr_value")
        if self.pr_status=="PR_NOT_JUSTIFIABLE" and self.pr_value is not None:raise ValueError("PR_NOT_JUSTIFIABLE requiere pr_value=null")
        if self.pr_value is not None and self.currency is None:raise ValueError("Un PR requiere moneda")
        if len(self.reference_set)!=self.counts.n_selected:raise ValueError("reference_set debe coincidir con n_selected")
        if self.counts.n_selected==0 and self.pr_status!="PR_NOT_JUSTIFIABLE":raise ValueError("N_SELECTED=0 requiere PR_NOT_JUSTIFIABLE")
        if self.counts.n_selected==1 and self.pr_status=="PR_AVAILABLE":raise ValueError("N_SELECTED=1 no puede producir PR_AVAILABLE")
        return self
__all__=["AggregationMethod","ComparabilityStatus","EconomicBasisAssessment","EconomicBasisEvidence","EconomicBasisStatus","EconomicDimension","PriceEconomicBasisComparison","NormalizationBasis","NormalizationRecord","PriceConversionInstruction","NormalizationStatus","PRStatus","PriceCounts","PriceIntelligenceAssessmentContext","PriceIntelligenceInput","PriceIntelligenceResult","PriceReference","PriceReferenceAssessment","RepresentativenessStatus","SufficiencyStatus","TemporalStatus"]