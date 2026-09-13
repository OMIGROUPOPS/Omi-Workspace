import unittest
import numpy as np
from absorption_residual_model import (RankDesign, RidgeFamily, game_weights,
    translated_scores, clustered_interval, promotion_bar)


class ResidualTests(unittest.TestCase):
    def test_game_weights_not_receipt_weights(self):
        w=game_weights(['a','a','a','b'])
        self.assertAlmostEqual(w[:3].sum(), w[3])

    def test_transform_never_learns_from_query(self):
        d=RankDesign.fit(np.asarray([[0.],[1.],[2.]]), ['first_own'], [.25,.5,.75])
        z=d.transform(np.asarray([[100.],[np.nan]]))
        self.assertEqual(z[0,0],1)
        self.assertEqual(z[1,1],1)
        np.testing.assert_equal(d.sorted_values[0], [0,1,2])

    def test_zero_control_exact(self):
        f=RidgeFamily.fit(np.array([[0.],[1.],[2.],[3.]]),[1,2,3,4],['a','b','c','d'],['first_own'],[.25,.5,.75])
        np.testing.assert_equal(f.predict(np.array([[9.],[np.nan]]),'ZERO'), [0,0])

    def test_constant_and_empty_observed_predictors(self):
        f=RidgeFamily.fit(np.array([[np.nan],[np.nan]]),[2,2],['a','b'],['book'],[.25,.5,.75])
        np.testing.assert_allclose(f.predict(np.array([[np.nan]]),'OLS'),[2])

    def test_ridge_is_deterministic_and_training_only(self):
        x=np.arange(8,dtype=float)[:,None]
        a=RidgeFamily.fit(x, np.arange(8),list('abcdefgh'),['book'],[.25,.5,.75])
        b=RidgeFamily.fit(x, np.arange(8),list('abcdefgh'),['book'],[.25,.5,.75])
        np.testing.assert_array_equal(a.predict(x,'OLS'),b.predict(x,'OLS'))
        self.assertLess(np.abs(a.predict(x,'OLS')-np.arange(8)).max(),1e-10)

    def test_distribution_translates_not_point_mass(self):
        row=dict(values=[1,3],weights=[1,1],q=1,target=2)
        s=translated_scores(row,1)
        self.assertEqual(s['q'],2)
        self.assertEqual(s['mae'],0)
        self.assertEqual(s['crps'],.5)

    def test_date_cluster_ci_and_no_single_date_claim(self):
        games=[dict(event=str(i),date=str(i//2),variant=0,control=1) for i in range(10)]
        a=clustered_interval(games,seed_material='test',draws=100,comparisons=36)
        b=clustered_interval(games,seed_material='test',draws=100,comparisons=36)
        self.assertEqual(a,b)
        self.assertEqual(a['interval'],[-1,-1])
        self.assertIsNone(clustered_interval(games[:2],seed_material='test',draws=100,comparisons=36)['interval'])

    def test_bar_requires_each_condition(self):
        mae=dict(n_games=100,delta=-.1,interval=[-.2,-.01])
        crps=dict(delta=0)
        self.assertTrue(promotion_bar(mae,crps,minimum_games=100,minimum_effect=.1,coverage_preserved=True,unsafe=False)['pass_bar'])
        self.assertFalse(promotion_bar(mae,dict(delta=.01),minimum_games=100,minimum_effect=.1,coverage_preserved=True,unsafe=False)['pass_bar'])


if __name__=='__main__':
    unittest.main()
