"""Preserve old input bytes while aligning canonical observer metadata.

The original deep verifier requires playback and validated cases to agree even
on observation-only fields. Only the missing existing ground64 Port metadata
is copied here; geometry, controls, initial conditions and all raw stay fixed.
"""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
import shutil
from pcg.migration import core, physics


def main():
    for row in core.read(core.REPO/'feedback/manual-review/implementation-results/batch-001/authorization/handoff-v1.json')['rows']:
        folder=core.REPO/row['outputDirectory'];history=folder/'revisions/observer-metadata-v2'
        if history.exists():raise ValueError('immutable_metadata_history_exists')
        before=core.read(folder/'cases.json');after=core.read(folder/'physics-input-cases.json')
        strip=lambda d:[{k:v for k,v in c.items()if k!='block_ports'}for c in d['cases']]
        assert strip(before)==strip(after)
        history.mkdir(parents=True)
        for name in ('cases.json','frozen.json','boundary-binding.json'):shutil.copy2(folder/name,history/name)
        core.write(folder/'cases.json',after)
        frozen=core.read(folder/'frozen.json');frozen['cases']=physics.artifact(folder/'cases.json')
        frozen['observerOnlyRevision']=dict(previousFrozen=physics.artifact(history/'frozen.json'),previousCases=physics.artifact(history/'cases.json'),
            changes=['block_ports aperture/grid/crossing_offset only'],geometryOrControlChanged=False)
        core.write(folder/'frozen.json',frozen)
        boundary=core.read(folder/'boundary-binding.json');boundary['before']=physics.artifact(history/'cases.json');core.write(folder/'boundary-binding.json',boundary)
        core.write(folder/'metadata-reconciliation.json',dict(source=physics.artifact(__file__),before=physics.artifact(history/'cases.json'),
            after=physics.artifact(folder/'cases.json'),physicsInput=physics.artifact(folder/'physics-input-cases.json'),
            previousBoundaryBinding=physics.artifact(history/'boundary-binding.json'),gameplayProgramEqual=True,
            historicalBindingResolution='References to the former cases.json SHA resolve to the byte-identical revisions/observer-metadata-v2/cases.json; original experiment inputs and snapshots are unmodified.'))


if __name__=='__main__':main()
