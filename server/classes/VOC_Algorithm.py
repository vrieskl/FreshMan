VOC_ALGORITHM_SAMPLING_INTERVAL = 1.
VOC_ALGORITHM_INITIAL_BLACKOUT = 45.
VOC_ALGORITHM_VOC_INDEX_GAIN = 230.
VOC_ALGORITHM_SRAW_STD_INITIAL = 50.
VOC_ALGORITHM_SRAW_STD_BONUS = 220.
VOC_ALGORITHM_TAU_MEAN_VARIANCE_HOURS = 12.
VOC_ALGORITHM_TAU_INITIAL_MEAN = 20.
VOC_ALGORITHM_INITIAL_DURATION_MEAN = 3600. * 0.75
VOC_ALGORITHM_INITIAL_TRANSITION_MEAN = 0.01
VOC_ALGORITHM_TAU_INITIAL_VARIANCE = 2500.
VOC_ALGORITHM_INITIAL_DURATION_VARIANCE = (3600. * 1.45)
VOC_ALGORITHM_INITIAL_TRANSITION_VARIANCE = 0.01
VOC_ALGORITHM_GATING_THRESHOLD = 340.
VOC_ALGORITHM_GATING_THRESHOLD_INITIAL = 510.
VOC_ALGORITHM_GATING_THRESHOLD_TRANSITION = 0.09
VOC_ALGORITHM_GATING_MAX_DURATION_MINUTES = (60. * 3.)
VOC_ALGORITHM_GATING_MAX_RATIO = 0.3
VOC_ALGORITHM_SIGMOID_L = 500.
VOC_ALGORITHM_SIGMOID_K = (-0.0065)
VOC_ALGORITHM_SIGMOID_X0 = 213.
VOC_ALGORITHM_VOC_INDEX_OFFSET_DEFAULT = 100.
VOC_ALGORITHM_LP_TAU_FAST = 20.0
VOC_ALGORITHM_LP_TAU_SLOW = 500.0
VOC_ALGORITHM_LP_ALPHA = (-0.2)
VOC_ALGORITHM_PERSISTENCE_UPTIME_GAMMA = (3. * 3600.)
VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__GAMMA_SCALING = 64.
VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__FIX16_MAX = 32767.
FIX16_MAXIMUM = 0x7FFFFFFF
FIX16_MINIMUM = 0x80000000
FIX16_OVERFLOW = 0x80000000
FIX16_ONE = 0x00010000


class DFRobot_VOC_ALGORITHMParams:
    def __init__(self):
        self.mvoc_index_offset = 0
        self.mtau_mean_variance_hours = 0
        self.mgating_max_duration_minutes = 0
        self.msraw_std_initial = 0
        self.muptime = 0
        self.msraw = 0
        self.mvoc_index = 0
        self.m_mean_variance_estimator_gating_max_duration_minutes = 0
        self.m_mean_variance_estimator_initialized = 0
        self.m_mean_variance_estimator_mean = 0
        self.m_mean_variance_estimator_sraw_offset = 0
        self.m_mean_variance_estimator_std = 0
        self.m_mean_variance_estimator_gamma = 0
        self.m_mean_variance_estimator_gamma_initial_mean = 0
        self.m_mean_variance_estimator_gamma_initial_variance = 0
        self.m_mean_variance_estimator_gamma_mean = 0
        self.m_mean_variance_estimator__gamma_variance = 0
        self.m_mean_variance_estimator_uptime_gamma = 0
        self.m_mean_variance_estimator_uptime_gating = 0
        self.m_mean_variance_estimator_gating_duration_minutes = 0
        self.m_mean_variance_estimator_sigmoid_l = 0
        self.m_mean_variance_estimator_sigmoid_k = 0
        self.m_mean_variance_estimator_sigmoid_x0 = 0
        self.m_mox_model_s_raw_mean = 0
        self.m_sigmoid_scaled_offset = 0
        self.m_adaptive_lowpass_a1 = 0
        self.m_adaptive_lowpass_a2 = 0
        self.m_adaptive_lowpass_initialized = 0
        self.m_adaptive_lowpass_x1 = 0
        self.m_adaptive_lowpass_x2 = 0
        self.m_adaptive_lowpass_x3 = 0


class DFRobot_VOC_ALGORITHM:

    def __init__(self):
        self.params = DFRobot_VOC_ALGORITHMParams()

    @staticmethod
    def _f16(x):
        if x >= 0:
            return int(x * 65536.0 + 0.5)
        else:
            return int(x * 65536.0 - 0.5)

    @staticmethod
    def _fix16_from_int(a):
        return int(a * FIX16_ONE)

    @staticmethod
    def _fix16_cast_to_int(a):
        return int(a) >> 16

    @staticmethod
    def _fix16_mul(in_arg0, in_arg1):
        in_arg0 = int(in_arg0)
        in_arg1 = int(in_arg1)
        A = (in_arg0 >> 16)
        if in_arg0 < 0:
            B = (in_arg0 & 0xFFFFFFFF) & 0xFFFF
        else:
            B = in_arg0 & 0xFFFF
        C = (in_arg1 >> 16)
        if in_arg1 < 0:
            D = (in_arg1 & 0xFFFFFFFF) & 0xFFFF
        else:
            D = in_arg1 & 0xFFFF
        AC = (A * C)
        AD_CB = (A * D + C * B)
        BD = (B * D)
        product_hi = (AC + (AD_CB >> 16))
        ad_cb_temp = (AD_CB << 16) & 0xFFFFFFFF
        product_lo = (BD + ad_cb_temp) & 0xFFFFFFFF
        if product_lo < BD:
            product_hi = product_hi + 1
        if (product_hi >> 31) != (product_hi >> 15):
            return FIX16_OVERFLOW
        product_lo_tmp = product_lo & 0xFFFFFFFF
        product_lo = (product_lo - 0x8000) & 0xFFFFFFFF
        product_lo = (product_lo - ((product_hi & 0xFFFFFFFF) >> 31)) & 0xFFFFFFFF
        if product_lo > product_lo_tmp:
            product_hi = product_hi - 1
        result = (product_hi << 16) | (product_lo >> 16)
        result += 1
        return result

    @staticmethod
    def _fix16_div(a, b):
        a = int(a)
        b = int(b)
        if b == 0:
            return FIX16_MINIMUM
        if a >= 0:
            remainder = a
        else:
            remainder = (a * (-1)) & 0xFFFFFFFF
        if b >= 0:
            divider = b
        else:
            divider = (b * (-1)) & 0xFFFFFFFF
        quotient = 0
        bit = 0x10000
        while divider < remainder:
            divider = divider << 1
            bit <<= 1
        if not bit:
            return FIX16_OVERFLOW
        if divider & 0x80000000:
            if remainder >= divider:
                quotient |= bit
                remainder -= divider
            divider >>= 1
            bit >>= 1
        while bit and remainder:
            if remainder >= divider:
                quotient |= bit
                remainder -= divider
            remainder <<= 1
            bit >>= 1
        if remainder >= divider:
            quotient += 1
        result = quotient
        if (a ^ b) & 0x80000000:
            if result == FIX16_MINIMUM:
                return FIX16_OVERFLOW
            result = -result
        return result

    @staticmethod
    def _fix16_sqrt(x):
        x = int(x)
        num = x & 0xFFFFFFFF
        result = 0
        bit = 1 << 30
        while bit > num:
            bit >>= 2
        for n in range(0, 2):
            while bit:
                if num >= result + bit:
                    num = num - (result + bit) & 0xFFFFFFFF
                    result = (result >> 1) + bit
                else:
                    result = (result >> 1)
                bit >>= 2
            if n == 0:
                if num > 65535:
                    num = (num - result) & 0xFFFFFFFF
                    num = ((num << 16) - 0x8000) & 0xFFFFFFFF
                    result = ((result << 16) + 0x8000) & 0xFFFFFFFF
                else:
                    num = ((num << 16) & 0xFFFFFFFF)
                    result = ((result << 16) & 0xFFFFFFFF)
                bit = 1 << 14
        if num > result:
            result += 1
        return result

    def _fix16_exp(self, x):
        x = int(x)
        exp_pos_values = [self._f16(2.7182818), self._f16(1.1331485), self._f16(1.0157477), self._f16(1.0019550)]
        exp_neg_values = [self._f16(0.3678794), self._f16(0.8824969), self._f16(0.9844964), self._f16(0.9980488)]
        if x >= self._f16(10.3972):
            return FIX16_MAXIMUM
        if x <= self._f16(-11.7835):
            return 0
        if x < 0:
            x = -x
            exp_values = exp_neg_values
        else:
            exp_values = exp_pos_values
        res = FIX16_ONE
        arg = FIX16_ONE
        for i in range(0, 4):
            while x >= arg:
                res = self._fix16_mul(res, exp_values[i])
                x -= arg
            arg >>= 3
        return res

    def VOC_ALGORITHM_init(self):
        self.params.mvoc_index_offset = (self._f16(VOC_ALGORITHM_VOC_INDEX_OFFSET_DEFAULT))
        self.params.mtau_mean_variance_hours = self._f16(VOC_ALGORITHM_TAU_MEAN_VARIANCE_HOURS)
        self.params.mgating_max_duration_minutes = self._f16(VOC_ALGORITHM_GATING_MAX_DURATION_MINUTES)
        self.params.msraw_std_initial = self._f16(VOC_ALGORITHM_SRAW_STD_INITIAL)
        self.params.muptime = self._f16(0.)
        self.params.msraw = self._f16(0.)
        self.params.mvoc_index = 0
        self._VOC_ALGORITHM__init_instances()

    def _VOC_ALGORITHM__init_instances(self):
        self._VOC_ALGORITHM__mean_variance_estimator__init()
        self._VOC_ALGORITHM__mean_variance_estimator__set_parameters(
            self._f16(VOC_ALGORITHM_SRAW_STD_INITIAL),
            self.params.mtau_mean_variance_hours,
            self.params.mgating_max_duration_minutes)
        self._VOC_ALGORITHM__mox_model__init()
        self._VOC_ALGORITHM__mox_model__set_parameters(
            self._VOC_ALGORITHM__mean_variance_estimator__get_std(),
            self._VOC_ALGORITHM__mean_variance_estimator__get_mean())
        self._VOC_ALGORITHM__sigmoid_scaled__init()
        self._VOC_ALGORITHM__sigmoid_scaled__set_parameters(self.params.mvoc_index_offset)
        self._VOC_ALGORITHM__adaptive_lowpass__init()
        self._VOC_ALGORITHM__adaptive_lowpass__set_parameters()

    def _VOC_ALGORITHM_get_states(self, state0, state1):
        state0 = self._VOC_ALGORITHM__mean_variance_estimator__get_mean()
        state1 = self._VOC_ALGORITHM__mean_variance_estimator__get_std()
        return state0, state1

    def _VOC_ALGORITHM_set_states(self, state0, state1):
        self._VOC_ALGORITHM__mean_variance_estimator__set_states(self.params, state0, state1)
        self.params.msraw = state0

    def _VOC_ALGORITHM_set_tuning_parameters(self, voc_index_offset, learning_time_hours, gating_max_duration_minutes,
                                             std_initial):
        self.params.mvoc_index_offset = self._fix16_from_int(voc_index_offset)
        self.params.mtau_mean_variance_hours = self._fix16_from_int(learning_time_hours)
        self.params.mgating_max_duration_minutes = self._fix16_from_int(gating_max_duration_minutes)
        self.params.msraw_std_initial = self._fix16_from_int(std_initial)
        self._VOC_ALGORITHM__init_instances()

    def VOC_ALGORITHM_process(self, sraw):
        if self.params.muptime <= self._f16(VOC_ALGORITHM_INITIAL_BLACKOUT):
            self.params.muptime = self.params.muptime + self._f16(VOC_ALGORITHM_SAMPLING_INTERVAL)
        else:
            if (sraw > 0) and (sraw < 65000):
                if sraw < 20001:
                    sraw = 20001
                elif sraw > 52767:
                    sraw = 52767
                self.params.msraw = self._fix16_from_int((sraw - 20000))
            self.params.mvoc_index = self._VOC_ALGORITHM__mox_model__process(self.params.msraw)
            self.params.mvoc_index = self._VOC_ALGORITHM__sigmoid_scaled__process(self.params.mvoc_index)
            self.params.mvoc_index = self._VOC_ALGORITHM__adaptive_lowpass__process(self.params.mvoc_index)
            if self.params.mvoc_index < self._f16(0.5):
                self.params.mvoc_index = self._f16(0.5)
            if self.params.msraw > self._f16(0.):
                self._VOC_ALGORITHM__mean_variance_estimator__process(self.params.msraw, self.params.mvoc_index)
                self._VOC_ALGORITHM__mox_model__set_parameters(self._VOC_ALGORITHM__mean_variance_estimator__get_std(),
                                                               self._VOC_ALGORITHM__mean_variance_estimator__get_mean())
        voc_index = self._fix16_cast_to_int((self.params.mvoc_index + self._f16(0.5)))
        return voc_index

    def _VOC_ALGORITHM__mean_variance_estimator__init(self):
        self._VOC_ALGORITHM__mean_variance_estimator__set_parameters(self._f16(0.), self._f16(0.), self._f16(0.))
        self._VOC_ALGORITHM__mean_variance_estimator___init_instances()

    def _VOC_ALGORITHM__mean_variance_estimator___init_instances(self):
        self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__init()

    def _VOC_ALGORITHM__mean_variance_estimator__set_parameters(self, std_initial, tau_mean_variance_hours,
                                                                gating_max_duration_minutes):
        self.params.m_mean_variance_estimator_gating_max_duration_minutes = gating_max_duration_minutes
        self.params.m_mean_variance_estimator_initialized = 0
        self.params.m_mean_variance_estimator_mean = self._f16(0.)
        self.params.m_mean_variance_estimator_sraw_offset = self._f16(0.)
        self.params.m_mean_variance_estimator_std = std_initial
        self.params.m_mean_variance_estimator_gamma = self._fix16_div(
            self._f16(
                (VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__GAMMA_SCALING * (VOC_ALGORITHM_SAMPLING_INTERVAL / 3600.))),
            (tau_mean_variance_hours + self._f16((VOC_ALGORITHM_SAMPLING_INTERVAL / 3600.))))
        self.params.m_mean_variance_estimator_gamma_initial_mean = self._f16(
            ((VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__GAMMA_SCALING * VOC_ALGORITHM_SAMPLING_INTERVAL) \
             / (VOC_ALGORITHM_TAU_INITIAL_MEAN + VOC_ALGORITHM_SAMPLING_INTERVAL)))
        self.params.m_mean_variance_estimator_gamma_initial_variance = self._f16(
            ((VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__GAMMA_SCALING * VOC_ALGORITHM_SAMPLING_INTERVAL) \
             / (VOC_ALGORITHM_TAU_INITIAL_VARIANCE + VOC_ALGORITHM_SAMPLING_INTERVAL)))
        self.params.m_mean_variance_estimator_gamma_mean = self._f16(0.)
        self.params.m_mean_variance_estimator__gamma_variance = self._f16(0.)
        self.params.m_mean_variance_estimator_uptime_gamma = self._f16(0.)
        self.params.m_mean_variance_estimator_uptime_gating = self._f16(0.)
        self.params.m_mean_variance_estimator_gating_duration_minutes = self._f16(0.)

    def _VOC_ALGORITHM__mean_variance_estimator__set_states(self, mean, std, uptime_gamma):
        self.params.m_mean_variance_estimator_mean = mean
        self.params.m_mean_variance_estimator_std = std
        self.params.m_mean_variance_estimator_uptime_gamma = uptime_gamma
        self.params.m_mean_variance_estimator_initialized = True

    def _VOC_ALGORITHM__mean_variance_estimator__get_std(self):
        return self.params.m_mean_variance_estimator_std

    def _VOC_ALGORITHM__mean_variance_estimator__get_mean(self):
        return self.params.m_mean_variance_estimator_mean + self.params.m_mean_variance_estimator_sraw_offset

    def _VOC_ALGORITHM__mean_variance_estimator___calculate_gamma(self, voc_index_from_prior):
        uptime_limit = self._f16((VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__FIX16_MAX - VOC_ALGORITHM_SAMPLING_INTERVAL))
        if self.params.m_mean_variance_estimator_uptime_gamma < uptime_limit:
            self.params.m_mean_variance_estimator_uptime_gamma = (
                    self.params.m_mean_variance_estimator_uptime_gamma + self._f16(VOC_ALGORITHM_SAMPLING_INTERVAL))

        if self.params.m_mean_variance_estimator_uptime_gating < uptime_limit:
            self.params.m_mean_variance_estimator_uptime_gating = (
                    self.params.m_mean_variance_estimator_uptime_gating + self._f16(VOC_ALGORITHM_SAMPLING_INTERVAL))

        self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__set_parameters(self._f16(1.), self._f16(
            VOC_ALGORITHM_INITIAL_DURATION_MEAN), self._f16(VOC_ALGORITHM_INITIAL_TRANSITION_MEAN))
        sigmoid_gamma_mean = self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__process(
            self.params.m_mean_variance_estimator_uptime_gamma)
        gamma_mean = (self.params.m_mean_variance_estimator_gamma + (self._fix16_mul(
            (self.params.m_mean_variance_estimator_gamma_initial_mean - self.params.m_mean_variance_estimator_gamma),
            sigmoid_gamma_mean)))
        gating_threshold_mean = (self._f16(VOC_ALGORITHM_GATING_THRESHOLD) + (self._fix16_mul(
            self._f16((VOC_ALGORITHM_GATING_THRESHOLD_INITIAL - VOC_ALGORITHM_GATING_THRESHOLD)),
            self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__process(
                self.params.m_mean_variance_estimator_uptime_gating))))
        self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__set_parameters(self._f16(1.), gating_threshold_mean,
                                                                               self._f16(
                                                                                   VOC_ALGORITHM_GATING_THRESHOLD_TRANSITION))

        sigmoid_gating_mean = self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__process(voc_index_from_prior)
        self.params.m_mean_variance_estimator_gamma_mean = (self._fix16_mul(sigmoid_gating_mean, gamma_mean))

        self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__set_parameters(self._f16(1.), self._f16(
            VOC_ALGORITHM_INITIAL_DURATION_VARIANCE), self._f16(VOC_ALGORITHM_INITIAL_TRANSITION_VARIANCE))

        sigmoid_gamma_variance = self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__process(
            self.params.m_mean_variance_estimator_uptime_gamma)

        gamma_variance = (self.params.m_mean_variance_estimator_gamma +
                          (self._fix16_mul((self.params.m_mean_variance_estimator_gamma_initial_variance
                                            - self.params.m_mean_variance_estimator_gamma),
                                           (sigmoid_gamma_variance - sigmoid_gamma_mean))))

        gating_threshold_variance = (self._f16(VOC_ALGORITHM_GATING_THRESHOLD) \
                                     + (self._fix16_mul(
                    self._f16((VOC_ALGORITHM_GATING_THRESHOLD_INITIAL - VOC_ALGORITHM_GATING_THRESHOLD)), \
                    self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__process(
                        self.params.m_mean_variance_estimator_uptime_gating))))

        self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__set_parameters(self._f16(1.), gating_threshold_variance,
                                                                               self._f16(
                                                                                   VOC_ALGORITHM_GATING_THRESHOLD_TRANSITION))

        sigmoid_gating_variance = self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__process(voc_index_from_prior)

        self.params.m_mean_variance_estimator__gamma_variance = (
            self._fix16_mul(sigmoid_gating_variance, gamma_variance))

        self.params.m_mean_variance_estimator_gating_duration_minutes = (
                self.params.m_mean_variance_estimator_gating_duration_minutes
                + (self._fix16_mul(self._f16((VOC_ALGORITHM_SAMPLING_INTERVAL / 60.)),
                                   ((self._fix16_mul((self._f16(1.) - sigmoid_gating_mean),
                                                     self._f16((1. + VOC_ALGORITHM_GATING_MAX_RATIO))))
                                    - self._f16(VOC_ALGORITHM_GATING_MAX_RATIO)))))

        if self.params.m_mean_variance_estimator_gating_duration_minutes < self._f16(0.):
            self.params.m_mean_variance_estimator_gating_duration_minutes = self._f16(0.)

        if ((
                self.params.m_mean_variance_estimator_gating_duration_minutes > self.params.m_mean_variance_estimator_gating_max_duration_minutes)):
            self.params.m_mean_variance_estimator_uptime_gating = self._f16(0.)

    def _VOC_ALGORITHM__mean_variance_estimator__process(self, sraw, voc_index_from_prior):
        if self.params.m_mean_variance_estimator_initialized == 0:
            self.params.m_mean_variance_estimator_initialized = 1
            self.params.m_mean_variance_estimator_sraw_offset = sraw
            self.params.m_mean_variance_estimator_mean = self._f16(0.)
        else:
            if (((self.params.m_mean_variance_estimator_mean >= self._f16(100.)) or (
                    self.params.m_mean_variance_estimator_mean <= self._f16(-100.)))):
                self.params.m_mean_variance_estimator_sraw_offset = (
                        self.params.m_mean_variance_estimator_sraw_offset + self.params.m_mean_variance_estimator_mean)
                self.params.m_mean_variance_estimator_mean = self._f16(0.)

            sraw = (sraw - self.params.m_mean_variance_estimator_sraw_offset)
            self._VOC_ALGORITHM__mean_variance_estimator___calculate_gamma(voc_index_from_prior)
            delta_sgp = (self._fix16_div((sraw - self.params.m_mean_variance_estimator_mean),
                                         self._f16(VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__GAMMA_SCALING)))
            if ((delta_sgp < self._f16(0.))):
                c = (self.params.m_mean_variance_estimator_std - delta_sgp)
            else:
                c = (self.params.m_mean_variance_estimator_std + delta_sgp)
            additional_scaling = self._f16(1.)
            if ((c > self._f16(1440.))):
                additional_scaling = self._f16(4.)
            self.params.m_mean_variance_estimator_std = self._fix16_mul(
                self._fix16_sqrt((self._fix16_mul(additional_scaling,
                                                  (self._f16(
                                                      VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__GAMMA_SCALING) - self.params.m_mean_variance_estimator__gamma_variance)))),
                self._fix16_sqrt(((self._fix16_mul(self.params.m_mean_variance_estimator_std,
                                                   (self._fix16_div(self.params.m_mean_variance_estimator_std,
                                                                    (self._fix16_mul(self._f16(
                                                                        VOC_ALGORITHM_MEAN_VARIANCE_ESTIMATOR__GAMMA_SCALING),
                                                                        additional_scaling))))))
                                  + (self._fix16_mul((self._fix16_div(
                            (self._fix16_mul(self.params.m_mean_variance_estimator__gamma_variance, delta_sgp)),
                            additional_scaling))
                            , delta_sgp)))))
            self.params.m_mean_variance_estimator_mean = (self.params.m_mean_variance_estimator_mean + (
                self._fix16_mul(self.params.m_mean_variance_estimator_gamma_mean, delta_sgp)))

    def _VOC_ALGORITHM__mean_variance_estimator___sigmoid__init(self):
        self._VOC_ALGORITHM__mean_variance_estimator___sigmoid__set_parameters(self._f16(0.), self._f16(0.),
                                                                               self._f16(0.))

    def _VOC_ALGORITHM__mean_variance_estimator___sigmoid__set_parameters(self, L, X0, K):
        self.params.m_mean_variance_estimator_sigmoid_l = L
        self.params.m_mean_variance_estimator_sigmoid_k = K
        self.params.m_mean_variance_estimator_sigmoid_x0 = X0

    def _VOC_ALGORITHM__mean_variance_estimator___sigmoid__process(self, sample):
        x = (self._fix16_mul(self.params.m_mean_variance_estimator_sigmoid_k,
                             (sample - self.params.m_mean_variance_estimator_sigmoid_x0)))
        if x < self._f16(-50.):
            return self.params.m_mean_variance_estimator_sigmoid_l
        elif x > self._f16(50.):
            return self._f16(0.)
        else:
            return (
                self._fix16_div(self.params.m_mean_variance_estimator_sigmoid_l, (self._f16(1.) + self._fix16_exp(x))))

    def _VOC_ALGORITHM__mox_model__init(self):
        self._VOC_ALGORITHM__mox_model__set_parameters(self._f16(1.), self._f16(0.))

    def _VOC_ALGORITHM__mox_model__set_parameters(self, SRAW_STD, SRAW_MEAN):
        self.params.m_mox_model_sraw_std = SRAW_STD
        self.params.m_mox_model_s_raw_mean = SRAW_MEAN

    def _VOC_ALGORITHM__mox_model__process(self, sraw):
        return (self._fix16_mul((self._fix16_div((sraw - self.params.m_mox_model_s_raw_mean), (
            -(self.params.m_mox_model_sraw_std + self._f16(VOC_ALGORITHM_SRAW_STD_BONUS))))),
                                self._f16(VOC_ALGORITHM_VOC_INDEX_GAIN)))

    def _VOC_ALGORITHM__sigmoid_scaled__init(self):
        self._VOC_ALGORITHM__sigmoid_scaled__set_parameters(self._f16(0.))

    def _VOC_ALGORITHM__sigmoid_scaled__set_parameters(self, offset):
        self.params.m_sigmoid_scaled_offset = offset

    def _VOC_ALGORITHM__sigmoid_scaled__process(self, sample):
        x = (self._fix16_mul(self._f16(VOC_ALGORITHM_SIGMOID_K), (sample - self._f16(VOC_ALGORITHM_SIGMOID_X0))))
        if x < self._f16(-50.):
            return self._f16(VOC_ALGORITHM_SIGMOID_L)
        elif x > self._f16(50.):
            return self._f16(0.)
        else:
            if sample >= self._f16(0.):
                shift = (self._fix16_div((self._f16(VOC_ALGORITHM_SIGMOID_L) - (
                    self._fix16_mul(self._f16(5.), self.params.m_sigmoid_scaled_offset))), self._f16(4.)))
                return ((self._fix16_div((self._f16(VOC_ALGORITHM_SIGMOID_L) + shift),
                                         (self._f16(1.) + self._fix16_exp(x)))) - shift)
            else:
                return (self._fix16_mul((self._fix16_div(self.params.m_sigmoid_scaled_offset,
                                                         self._f16(VOC_ALGORITHM_VOC_INDEX_OFFSET_DEFAULT))),
                                        (self._fix16_div(self._f16(VOC_ALGORITHM_SIGMOID_L),
                                                         (self._f16(1.) + self._fix16_exp(x))))))

    def _VOC_ALGORITHM__adaptive_lowpass__init(self):
        self._VOC_ALGORITHM__adaptive_lowpass__set_parameters()

    def _VOC_ALGORITHM__adaptive_lowpass__set_parameters(self):
        self.params.m_adaptive_lowpass_a1 = self._f16(
            (VOC_ALGORITHM_SAMPLING_INTERVAL / (VOC_ALGORITHM_LP_TAU_FAST + VOC_ALGORITHM_SAMPLING_INTERVAL)))
        self.params.m_adaptive_lowpass_a2 = self._f16(
            (VOC_ALGORITHM_SAMPLING_INTERVAL / (VOC_ALGORITHM_LP_TAU_SLOW + VOC_ALGORITHM_SAMPLING_INTERVAL)))
        self.params.m_adaptive_lowpass_initialized = 0

    def _VOC_ALGORITHM__adaptive_lowpass__process(self, sample):
        if self.params.m_adaptive_lowpass_initialized == 0:
            self.params.m_adaptive_lowpass_x1 = sample
            self.params.m_adaptive_lowpass_x2 = sample
            self.params.m_adaptive_lowpass_x3 = sample
            self.params.m_adaptive_lowpass_initialized = 1
        self.params.m_adaptive_lowpass_x1 = ((self._fix16_mul((self._f16(1.) - self.params.m_adaptive_lowpass_a1),
                                                              self.params.m_adaptive_lowpass_x1)) + (
                                                 self._fix16_mul(self.params.m_adaptive_lowpass_a1, sample)))

        self.params.m_adaptive_lowpass_x2 = ((self._fix16_mul((self._f16(1.) - self.params.m_adaptive_lowpass_a2),
                                                              self.params.m_adaptive_lowpass_x2)) + (
                                                 self._fix16_mul(self.params.m_adaptive_lowpass_a2, sample)))

        abs_delta = (self.params.m_adaptive_lowpass_x1 - self.params.m_adaptive_lowpass_x2)

        if abs_delta < self._f16(0.):
            abs_delta = (-abs_delta)
        F1 = self._fix16_exp((self._fix16_mul(self._f16(VOC_ALGORITHM_LP_ALPHA), abs_delta)))
        tau_a = ((self._fix16_mul(self._f16((VOC_ALGORITHM_LP_TAU_SLOW - VOC_ALGORITHM_LP_TAU_FAST)), F1)) + self._f16(
            VOC_ALGORITHM_LP_TAU_FAST))
        a3 = (self._fix16_div(self._f16(VOC_ALGORITHM_SAMPLING_INTERVAL),
                              (self._f16(VOC_ALGORITHM_SAMPLING_INTERVAL) + tau_a)))
        self.params.m_adaptive_lowpass_x3 = (
                (self._fix16_mul((self._f16(1.) - a3), self.params.m_adaptive_lowpass_x3)) + (
            self._fix16_mul(a3, sample)))
        return self.params.m_adaptive_lowpass_x3
