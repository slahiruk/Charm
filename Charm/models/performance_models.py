from collections import defaultdict

from Charm.base.sheet import *
from Charm.models import MathModel
from Charm.models import RiskFunctionCollection


class BasePerformanceModel():
    def __init__(self):
        self.given = defaultdict()
        self.index = defaultdict()
        self.target = []

    def dict2list(self, k2v):
        return list(k2v.items())

    def get_nominal(self, uv):
        if isinstance(uv, UncertainFunction):
            return uv.mean
        else:
            return uv

    def compute(self, sheet, name=None, ext=None):
        ext_list = ext.gen_feed() if ext else []
        given = self.dict2list(self.given) + ext_list
        target = self.target
        bounds = self.index
        logging.debug('Evaluating --\n\tGive: {}\n\tIndex: {}\n\tTarget: {}'.format(
            given, bounds, target))
        # Sets up the computation.
        sheet.addPreds(given=given, bounds=bounds, response=target)
        # Result is a map: responsive metric -> value.
        result = sheet.compute()
        if name:
            assert name in result
            result = result[name]
        return result
    
    def add_index(self, idx_base, lower, upper):
        """ Adds index to the system.

        Args:
            idx_base: base symbol of the index.
            lower: lower bound value of the index.
            upper: upper bound value of the idex.
        """
        assert lower is not None and upper is not None
        self.index[idx_base] = (lower, upper)

    def add_given(self, name, val):
        """ Adds given variable to the system.

        Args:
            name: symbol of the variable.
            val: value to set it to.
        """
        self.given[name] = val

    def add_target(self, name):
        """ Adds target variable to the system.

        Args:
            name: symbol of the target variable.
        """
        self.target.append(name)

    def clear_index(self):
        self.index = {}

    def clear_given(self):
        self.given = {}

    def clear_target(self):
        self.target = []

    def clear(self):
        self.clear_index()
        self.clear_given()
        self.clear_target()

class HillMartyPerformanceModel(BasePerformanceModel):
    area = 256
    perf_target = 'speedup'
    energy_target = 'energy'
    #dbg_sum = 'dbg_sum'
    #dbg_sum_perf = 'dbg_sum_perf'
    #dbg_condmax = 'dbg_condmax'
    designs = [8, 16, 32, 64, 128, 256]
    def __init__(self, selected_model='hete',
            risk_function=RiskFunctionCollection.funcs['quad'],
            use_energy=False):
        BasePerformanceModel.__init__(self)
        all_syms = (MathModel.index_syms +
                MathModel.config_syms +
                MathModel.perf_syms +
                MathModel.stat_syms +
                MathModel.power_syms +
                MathModel.debug_syms)
        # Prepare syms and equations for all computing sheets.
        self.sheet1 = Sheet() # Computes final resposives.
        self.sheet2 = Sheet() # Computes core performance.
        self.sheet3 = Sheet() # Computes core num.
        self.sheet4 = Sheet() # Computes core power.
        self.sheet1.addSyms(all_syms)
        self.sheet2.addSyms(all_syms)
        self.sheet3.addSyms(all_syms)
        self.sheet4.addSyms(all_syms)
        self.sheet1.addFuncs(MathModel.custom_funcs)
        self.sheet2.addFuncs(MathModel.custom_funcs)
        self.sheet3.addFuncs(MathModel.custom_funcs)
        self.sheet4.addFuncs(MathModel.custom_funcs)
        if selected_model == 'symmetric':
            model = MathModel.symm_exprs
        elif selected_model == 'asymmetric':
            model = MathModel.asymm_exprs
        elif selected_model == 'dynamic':
            model = MathModel.dynamic_exprs
        elif selected_model == 'hete':
            model = (MathModel.hete_exprs if not use_energy
                    else MathModel.hete_exprs + MathModel.hete_power_exprs)
        else:
            raise ValueError('Unrecgonized model: {}'.format(selected_model))

        self.sheet1.addExprs(MathModel.common_exprs +
                MathModel.debug_exprs + model)
        self.sheet2.addExprs(MathModel.common_exprs +
                MathModel.debug_exprs + model)
        self.sheet3.addExprs(MathModel.common_exprs +
                MathModel.debug_exprs + model)
        self.sheet4.addExprs(MathModel.common_exprs +
                MathModel.debug_exprs + model)

        self.core_perf_cache = {}
        self.core_num_cache = {}
        self.core_power_cache = {}
        self.risk_func = risk_function
        self.use_energy = use_energy

    def dump(self):
        # Dump all expressions.
        self.sheet1.dump()
        # Dump risk function used.
        print((self.risk_func))

    def clear_caches(self):
        self.core_perf_cache = {}
        self.core_num_cache = {}
        self.core_power_cache = {}

    def get_risk(self, ref, d2perf):
        """ Compute risk for d2perf w.r.t. ref

        Args:
            ref: reference performance bar
            d2perf: performance array-like

        Returns:
            single float (mean risk)
        """
        return {k: self.risk_func.get_risk(ref, v) for k, v in list(d2perf.items())}

    def get_mean(self, d2uc):
        """ Extracts mean performance.
        """
        return {k: self.get_numerical(v) for k, v in list(d2uc.items())}

    def get_std(self, d2uc):
        return {k: np.sqrt(self.get_var(v)) for k, v in list(d2uc.items())}

    def apply_design(self, candidate, app):
        """ Try on a certain given design candidate.

        Args:
            candidate: design point
            app: application to solve.

        Returns:
            perf: result performance distribution.
        """
        assert len(candidate) == len(self.designs)
        area_left = self.__class__.area - sum([x * y for x, y in zip(candidate, self.designs)])
        assert area_left >= 0
        logging.info('PerfModel -- Evaluating design: {} ({})'.format(candidate, area_left))

        # Compute actual num for all cores.
        if area_left in self.designs:
            # To hit in the core_num_cache, we must generates the exact same
            # candidate, otherwise [0, 1, 0] (16) would be different from
            # [0, 2, 0] (0).
            candidate[self.designs.index(area_left)] += 1
        else:
            # If it is not a predefined core type, compute its num separately.
            self.compute_core_num(len(self.designs),
                    area_left, 1 if area_left else 0)
        for i, (size_i, num_i) in enumerate(zip(self.designs, candidate)):
            self.compute_core_num(i, size_i, num_i)

        # Compute perf for the left-over core. This will hit in the
        # core_perf_cache as long as the core size matches.
        self.compute_core_perf(len(self.designs), area_left)
        if self.use_energy:
            self.compute_core_power(len(self.designs), area_left)

        result = self.compute(self.sheet1, app)
        perf = result[self.perf_target]
        energy = result[self.energy_target] if self.use_energy else ''
        logging.info('PerfModel -- Result:\n\t{}, {}'.format(perf, energy))
        return perf

    def iter_through_design(self, d2perf, ith, stop, candidate, app):
        """ Place cores on chip, or evaluate a chip when a configuration has been selected.

        Args:
            d2perf: result, tuple(candidate) -> perf distribution.
            ith: the i-th design under inspection.
            stop: when to stop considering more designs.
            candidate: current candidate core placement list.
            app: application to solve.

        Returns:
            d2perf
        """
        area_left = self.__class__.area - sum(
                [x * y for x, y in zip(candidate, self.designs)])
        assert(area_left >= 0)
        if ith == stop:
            # We have a candidate configuration.
            tag = tuple(candidate + [area_left])
            d2perf[tag] = self.apply_design(candidate, app)
        else:
            # If we are still trying to place a core.
            d_cur = self.designs[ith]
            i = 0
            while (i < area_left/self.designs[ith]+1):
                candidate[ith] = i
                self.iter_through_design(d2perf, ith+1, stop, candidate, app)
                candidate[ith] = 0
                # We double the number of cores every time.
                i = 1 if i == 0 else i << 1

    def compute_core_num(self, i, d, n):
        target = 'core_num_'+str(i)

        # Try to get it from cache if possible.
        if ((d, n) in self.core_num_cache):
            logging.debug('Getting {} of ({}, {}) from cache'.format(target, d, n))
            self.add_given(target, self.core_num_cache[(d, n)])
            return

        # If we haven't computed this already.
        logging.debug('Computing {} of ({}, {})'.format(target, d, n))
        design_name = 'core_design_size_'+str(i)
        given = [(design_name, d)]
        design_name = 'core_design_num_'+str(i)
        given += [(design_name, n)]

        response = [target]

        self.sheet3.clear()
        self.sheet3.addPreds(given=given, response=response)
        result = self.sheet3.compute()
        num = result[target]
        self.add_given(target, num)
        self.core_num_cache[(d, n)] = num
        logging.debug('Caching {}: {}'.format(target, num))

    def compute_core_perf(self, i, d):
        target = 'core_perf_'+str(i)
        # Try to get it from cache if possible.
        if d in self.core_perf_cache:
            logging.debug('Getting {} of {} from cache'.format(target, d))
            self.add_given(target, self.core_perf_cache[d])
            return

        logging.debug('Computing perf for core {} of size {}'.format(i, d))
        design_name = 'core_design_size_'+str(i)
        given = [(design_name, d)]
        response = [target]

        self.sheet2.clear()
        self.sheet2.addPreds(given=given, response=response)
        result = self.sheet2.compute() # Map of all responsive results.
        perf = result[target]
        self.add_given(target, perf)
        self.core_perf_cache[d] = perf
        logging.debug('Caching {}: {}'.format(target, perf))

    def compute_core_power(self, i, d):
        if not d in self.core_perf_cache:
            self.compute_core_perf(i, d)

        target = 'core_power_'+str(i)
        # Try to get it from cache if possible.
        if d in self.core_power_cache:
            logging.debug('Getting {} of {} from cache'.format(target, d))
            self.add_given(target, self.core_power_cache[d])
            return

        logging.debug('Computing power for core {} of size {}'.format(i, d))
        design_name = 'core_perf_'+str(i)
        given = [(design_name, self.core_perf_cache[d])]
        response = [target]

        self.sheet4.clear()
        self.sheet4.addPreds(given=given, response=response)
        result = self.sheet4.compute() # Map of all responsive results.
        power = result[target]
        self.add_given(target, power)
        self.core_power_cache[d] = power
        logging.debug('Caching {}: {}'.format(target, power))

    def solve_system(self):
        self.clear_caches()
        given = []
        # Even though sheet1 doesn't need core_deisgn_size and core_design_num,
        # but our current implementation requires that it still has all those
        # variables as inputs because it will still try to solve equations that
        # depends on those variables. However, the values of those variables do
        # not matter to sheet1.
        for i, d in enumerate(self.designs + [0]):
            design_name = 'core_design_size_'+str(i)
            self.add_given(design_name, d)
            design_name = 'core_design_num_'+str(i)
            self.add_given(design_name, 0)
        given = self.dict2list(self.given)
        self.sheet2.addPreds(given=given, bounds=self.index,
                intermediates=[], response=[])
        self.sheet3.addPreds(given=given, bounds=self.index,
                intermediates=[], response=[])
        self.sheet4.addPreds(given=given, bounds=self.index,
                intermediates=[], response=[])
        # Compute fixed-design core perfs here. These are computed
        # only once before the DSE.
        for i, d in enumerate(self.designs):
            self.compute_core_perf(i, d)
            if self.use_energy:
                self.compute_core_power(i, d)

    def get_perf(self, app):
        """ Computes peformance distribution over a single app.
        """
        d2perf = defaultdict()
        n_designs = len(self.designs)
        candidate = [0] * n_designs
        self.add_index('i', 0, len(self.designs)+1)
        self.add_target(self.perf_target)
        self.solve_system()
        if self.use_energy:
            self.add_target(self.energy_target)
        self.iter_through_design(d2perf, 0, n_designs, candidate, app)
        return d2perf

    def print_latex(self):
        self.sheet1.printLatex()

class LogCAPerformanceModel(BasePerformanceModel):
    def __init__(self, risk_function=RiskFunctionCollection.funcs['quad']):
        BasePerformanceModel.__init__(self)
        self.sheet1 = Sheet() # Computes speedup
        # Sets up symbols.
        all_syms = (MathModel.index_syms +
                MathModel.logca_syms)
        self.sheet1.addSyms(all_syms)
        # Sets up functions.
        self.sheet1.addFuncs(MathModel.custom_funcs)
        # Sets up euqations.
        model = MathModel.gid_logca_exprs
        self.sheet1.addExprs(model)
        # Sets up risk function.
        self.risk_func = risk_function

    def dump(self):
        self.sheet1.dump()
        print((self.risk_func))

    def dprint(self, var):
        self.sheet1.dprint(var)
