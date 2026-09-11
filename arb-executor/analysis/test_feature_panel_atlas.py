"""Exact-cache, cadence and numerical-repair tests; no population/engine run."""
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import feature_panel_atlas as atlas
import feature_panel_atlas_optimizer as opt
import feature_panel_model as model
from test_feature_panel_bench import pair, Sampler, CONTRACT, kernel
import feature_panel_bench as bench


class AtlasTests(unittest.TestCase):
    def test_exact_clock_and_span_are_cache_keys(self):
        q=pair('q','2026-05-01',1000,1240)
        calls=[]
        def sample(p,g):
            calls.append(g.copy())
            return np.repeat(g[:,None,None],4,axis=2)
        cache=atlas.ExactStateCache(sample,'source',4096)
        gates=np.asarray([1.,np.nextafter(1.,2.),-0.,0.])
        first=cache.sample(q,gates)
        np.testing.assert_array_equal(first,cache.sample(q,gates))
        self.assertEqual(cache.misses,4)
        self.assertEqual(cache.hits,4)
        self.assertEqual(len(calls),1)
        changed=pair('q','2026-05-01',1000,1300)
        cache.sample(changed,gates)
        self.assertEqual(cache.misses,8)
        self.assertEqual(np.signbit(first[2,0,0]),True)

    def test_eviction_does_not_change_values(self):
        q=pair('q','2026-05-01',1000,1240)
        sampler=Sampler()
        cache=atlas.ExactStateCache(sampler.sample,'source',32)
        gates=np.asarray([3.,1.])
        np.testing.assert_equal(cache.sample(q,gates),sampler.sample(q,gates))
        np.testing.assert_equal(cache.sample(q,gates[::-1]),sampler.sample(q,gates[::-1]))

    def test_gate_projector_excludes_between_gate_receipts(self):
        members=[pair('m','2026-04-01',0,240)]
        q=pair('q','2026-05-01',1000,1240)
        k=kernel()
        got=list(atlas.AtlasProjector(members,Sampler(),CONTRACT,k,batch_size=2).receipts(q,'RECEIPT-SIM'))
        expected=list(atlas.BASE_PROJECTOR(members,Sampler(),CONTRACT,k,batch_size=2).receipts(q,'GATE-SIM'))
        self.assertEqual([x.baseline['source_gate_minutes'] for x in got],[3,1])
        for a,b in zip(got,expected):
            self.assertEqual(a.baseline,b.baseline)
            np.testing.assert_equal(a.levels,b.levels)

    def test_polish_does_not_accept_objective_stall_as_convergence(self):
        def objective(beta):
            d=beta-np.asarray([.4,.7])
            return 1.+float(np.dot(d,d)),2*d
        options=model.NumericalOptions()
        beta,report=opt.polish(objective,np.asarray([.400000035,.70000004]),options)
        self.assertEqual(report['status'],'PROJECTED_GRADIENT_CONVERGED')
        self.assertLessEqual(report['projected_gradient_max'],options.gradient_tolerance)
        np.testing.assert_allclose(beta,[.4,.7],atol=options.gradient_tolerance,rtol=0)

    def test_boundary_kkt_and_determinism(self):
        def objective(beta):return float(np.dot(beta+1,beta+1)),2*(beta+1)
        a=opt.polish(objective,np.asarray([.2]),model.NumericalOptions())
        b=opt.polish(objective,np.asarray([.2]),model.NumericalOptions())
        np.testing.assert_array_equal(a[0],b[0]);self.assertEqual(a[1],b[1])
        self.assertEqual(a[0][0],0)
        self.assertEqual(a[1]['status'],'PROJECTED_GRADIENT_CONVERGED')

    def test_empty_fit_is_explicit_not_converged_feature_fit(self):
        report=opt.fit_joint_model([],['a']).report
        self.assertEqual(report['optimizer_outcome'],'NO_TRAINING')

    def test_full_bench_source_binding_not_mutated(self):
        original=bench.FeatureProjector
        with atlas.adapter('scope',4096):
            self.assertIs(bench.FeatureProjector,atlas.AtlasProjector)
        self.assertIs(bench.FeatureProjector,original)

    def test_small_population_gate_only_and_twice_identical(self):
        from test_feature_panel_parallel import population_fixture
        from feature_panel_execution import compact_sampler_copy
        import feature_panel_run as run
        with tempfile.TemporaryDirectory() as directory:
            for name in ('one','two'):
                with atlas.adapter('same source',1024*1024):
                    pairs,sampler,baseline,spec=population_fixture()
                    sampler=compact_sampler_copy(sampler)
                    receipt,board=bench.run_category(pairs,sampler,baseline,spec,'category',Path(directory)/name,
                        heldout_months=('2026-06',),batch_size=2,cache_budget_bytes=8*1024*1024,
                        source_registry={'fixture':'synthetic'},progress=lambda row:None)
                    self.assertGreater(sampler.state_cache.hits,0)
                    self.assertEqual(receipt['eligible_games'],7)
            run.compare_runs(Path(directory)/'one',Path(directory)/'two')


if __name__=='__main__':unittest.main()
