from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from test_documentary_payment_review import review_args, arguments, capture
from eios.core.documentary_payment_capture import DocumentaryMaterial, DocumentaryLocator
from eios.core.documentary_payment_review import build_documentary_payment_human_review
from eios.core.documentary_reviewer_designation import (
    CONDITIONS, DesignationDeclaration, DesignationObservation,
    DocumentaryReviewerDesignationLink, build_documentary_reviewer_designation_link,
    validate_designation_link_for_review,
)


@pytest.fixture
def link_args(review_args):
    review = build_documentary_payment_human_review(**review_args)
    company = review.to_payload()['capture']['finance_package']['finance_input']['snapshot']['company_scope']
    return dict(review=review, link_ref='synthetic-link', designation_ref='DESIG-2026-004-v2',
        designation_kind='SYNTHETIC', reviewer_ref=review_args['reviewer_ref'], company_scope=company,
        documents=(DocumentaryMaterial(document_ref='DESIG-2026-004-v2',
                    content=b'Synthetic test stand-in; not the uploaded PDF or a real mandate'),),
        declarations=(), observations=())


def locator():
    return DocumentaryLocator(document_ref='DESIG-2026-004-v2', page=1, section='Synthetic designation')


def positive(condition='PERSON_CORRESPONDENCE'):
    return DesignationObservation(condition=condition, outcome='DECLARED_CONSISTENT',
        note='Fictitious supplied comparison; not identity verification', locators=(locator(),))


def test_empty_and_partial_leave_pending(link_args):
    empty = build_documentary_reviewer_designation_link(**link_args)
    assert empty.pending_controls == CONDITIONS
    assert empty.to_payload()['review'] == link_args['review'].to_payload()
    link_args['observations'] = (positive(),)
    assert len(build_documentary_reviewer_designation_link(**link_args).pending_controls) == 6


def test_synthetic_terms_preserved_without_interpretation(link_args):
    texts = dict(PERSON='Carlos Ruiz Mateo; fictitious person, mapping declared for test only',
        COMPANY='Empresa Ejemplo SL; fictitious correspondence supplied explicitly',
        ROLE_AND_SCOPE='Responsable de administración/finanzas para esta revisión documental; sin resultados QTG',
        VALIDITY='01/09/2026–31/12/2026; timezone and endpoint interpretation not supplied',
        CONDITIONS='50 000 EUR por expediente; fictitious condition, not EIOS threshold',
        ISSUER='Laura Martínez Silva; fictitious CFO, no actual authority proof')
    link_args['declarations'] = tuple(DesignationDeclaration(field=k, text=v, locators=(locator(),)) for k, v in texts.items())
    link_args['observations'] = (DesignationObservation(condition='VALIDITY', outcome='NOT_ESTABLISHED',
        note='No universal instant boundary invented'),)
    result = build_documentary_reviewer_designation_link(**link_args).to_payload()
    assert {d['field']: d['text'] for d in result['declarations']} == texts
    assert result['designation_kind'] == 'SYNTHETIC'
    assert result['review']['capture']['case_kind'] == 'SYNTHETIC'
    assert result['observations'][0]['outcome'] == 'NOT_ESTABLISHED'
    assert 'ISSUER_AUTHORITY_SUPPORT' in result['pending_controls']


def test_negative_and_unknown_not_relabelled_success(link_args):
    link_args['observations'] = tuple(DesignationObservation(condition=c, outcome=o, note='Supplied limitation')
        for c, o in [('COMPANY_CORRESPONDENCE', 'DECLARED_INCONSISTENT'), ('VALIDITY', 'NOT_ESTABLISHED')])
    result = build_documentary_reviewer_designation_link(**link_args)
    assert len(result.pending_controls) == 5
    assert [o['outcome'] for o in result.to_payload()['observations']] == ['DECLARED_INCONSISTENT', 'NOT_ESTABLISHED']


@pytest.mark.parametrize('field,value', [('reviewer_ref', 'foreign'), ('company_scope', 'foreign'),
    ('designation_kind', 'DEMONSTRATED'), ('designation_ref', 'missing'), ('link_ref', ' '),
    ('documents', ()), ('observations', [])])
def test_invalid_targets_and_collections(link_args, field, value):
    link_args[field] = value
    with pytest.raises((TypeError, ValueError)):
        build_documentary_reviewer_designation_link(**link_args)


def test_duplicate_documents_and_conditions(link_args):
    link_args['documents'] *= 2
    with pytest.raises(ValueError, match='Duplicate'):
        build_documentary_reviewer_designation_link(**link_args)
    link_args['documents'] = link_args['documents'][:1]
    link_args['observations'] = (positive(), positive())
    with pytest.raises(ValueError, match='Duplicate'):
        build_documentary_reviewer_designation_link(**link_args)


@pytest.mark.parametrize('changes', [{'outcome': 'APTO'}, {'note': ' '}, {'locators': ()},
    {'locators': (DocumentaryLocator(document_ref='foreign', page=1, section='x'),)},
    {'locators': (locator().model_copy(update={'page': True}),)}])
def test_revalidate_observation_bypass(link_args, changes):
    link_args['observations'] = (positive().model_copy(update=changes),)
    with pytest.raises(ValueError):
        build_documentary_reviewer_designation_link(**link_args)


def test_revalidate_document_and_declaration(link_args):
    link_args['documents'] = (link_args['documents'][0].model_copy(update={'content': b''}),)
    with pytest.raises(ValidationError):
        build_documentary_reviewer_designation_link(**link_args)
    link_args['documents'] = (DocumentaryMaterial(document_ref='DESIG-2026-004-v2', content=b'test'),)
    link_args['declarations'] = (DesignationDeclaration.model_construct(field='PERSON', text='x', locators=()),)
    with pytest.raises(ValidationError):
        build_documentary_reviewer_designation_link(**link_args)


def test_immutable_export_and_source_changes(link_args, review_args):
    result = build_documentary_reviewer_designation_link(**link_args)
    exported = result.to_payload()
    exported['review']['capture']['bindings'].clear()
    exported['documents'].clear()
    assert result.to_payload()['review']['capture']['bindings']
    assert result.document_bytes(link_args['designation_ref']) == link_args['documents'][0].content
    with pytest.raises(KeyError):
        result.document_bytes('foreign')
    with pytest.raises(FrozenInstanceError):
        result._material = b'changed'
    with pytest.raises(TypeError):
        DocumentaryReviewerDesignationLink()
    validate_designation_link_for_review(result, link_args['review'])
    review_args['review_ref'] = 'changed-review'
    with pytest.raises(ValueError, match='different'):
        validate_designation_link_for_review(result, build_documentary_payment_human_review(**review_args))
    link_args['documents'] = (link_args['documents'][0].model_copy(update={'content': b'changed'}),)
    assert build_documentary_reviewer_designation_link(**link_args).fingerprint != result.fingerprint


def test_all_positive_declarations_never_emit_authority(link_args, monkeypatch):
    import eios.finance.provenance as provenance
    import eios.quality.gate as gate
    def forbidden(*args, **kwargs):
        raise AssertionError('No engines or QTG allowed')
    monkeypatch.setattr(provenance, 'run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr(gate, 'evaluate_quality', forbidden)
    link_args['observations'] = tuple(positive(c) for c in CONDITIONS)
    link_args['designation_kind'] = 'PRESENTED_OPERATIONAL'
    result = build_documentary_reviewer_designation_link(**link_args).to_payload()
    assert result['pending_controls'] == []
    assert result['review']['capture']['case_kind'] == 'SYNTHETIC'
    assert not {'authorized', 'quality_result', 'evidence_state'} & result.keys()
    assert result['assurance_scope'] == 'PRESENTED_DECLARATIONS_ONLY'
