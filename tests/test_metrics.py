import collections
import functools
import math

import pytest

from creme import metrics
from sklearn import metrics as sk_metrics


@pytest.mark.parametrize(
    'metric, sk_metric, y_true, y_pred',
    [
        (
            metrics.Precision(),
            sk_metrics.precision_score,
            [True, False, True, True, True],
            [True, True, False, True, True]
        ),
        (
            metrics.MacroPrecision(),
            functools.partial(sk_metrics.precision_score, average='macro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),
        (
            metrics.MicroPrecision(),
            functools.partial(sk_metrics.precision_score, average='micro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),

        (
            metrics.Recall(),
            sk_metrics.recall_score,
            [True, False, True, True, True],
            [True, True, False, True, True]
        ),
        (
            metrics.MacroRecall(),
            functools.partial(sk_metrics.recall_score, average='macro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),
        (
            metrics.MicroRecall(),
            functools.partial(sk_metrics.recall_score, average='micro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),

        (
            metrics.FBeta(beta=0.5),
            functools.partial(sk_metrics.fbeta_score, beta=0.5),
            [True, False, True, True, True],
            [True, True, False, True, True]
        ),
        (
            metrics.MicroFBeta(beta=0.5),
            functools.partial(sk_metrics.fbeta_score, beta=0.5, average='micro'),
            [0, 1, 0, 2, 2],
            [0, 0, 1, 1, 2]
        ),

        (
            metrics.F1(),
            sk_metrics.f1_score,
            [True, False, True, True, True],
            [True, True, False, True, True]
        ),
        (
            metrics.MicroF1(),
            functools.partial(sk_metrics.f1_score, average='micro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),

        (
            metrics.LogLoss(),
            sk_metrics.log_loss,
            [True, False, False, True],
            [0.9, 0.1, 0.2, 0.65]
        ),
        (
            metrics.CrossEntropy(),
            functools.partial(sk_metrics.log_loss, labels=[0, 1, 2]),
            [0, 1, 2, 2],
            [
                [0.29450637, 0.34216758, 0.36332605],
                [0.21290077, 0.32728332, 0.45981591],
                [0.42860913, 0.33380113, 0.23758974],
                [0.44941979, 0.32962558, 0.22095463]
            ]
        )
    ]
)
def test_metric(metric, sk_metric, y_true, y_pred):

    for i, (yt, yp) in enumerate(zip(y_true, y_pred)):

        if isinstance(yp, list):
            yp = dict(enumerate(yp))

        metric.update(yt, yp)

        if i >= 1:
            assert math.isclose(metric.get(), sk_metric(y_true[:i + 1], y_pred[:i + 1]))


@pytest.mark.parametrize(
    'metric, sk_metric, y_true, y_pred',
    [
        (
            metrics.RollingPrecision(3),
            sk_metrics.precision_score,
            [True, False, True, True, True],
            [True, True, False, True, True]
        ),
        (
            metrics.RollingMacroPrecision(3),
            functools.partial(sk_metrics.precision_score, average='macro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),
        (
            metrics.RollingMicroPrecision(3),
            functools.partial(sk_metrics.precision_score, average='micro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),
        (
            metrics.RollingRecall(3),
            sk_metrics.recall_score,
            [True, False, True, True, True],
            [True, True, False, True, True]
        ),
        (
            metrics.RollingMacroRecall(3),
            functools.partial(sk_metrics.recall_score, average='macro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),
        (
            metrics.RollingMicroRecall(3),
            functools.partial(sk_metrics.recall_score, average='micro'),
            [0, 1, 2, 2, 2],
            [0, 0, 2, 2, 1]
        ),
        (
            metrics.RollingFBeta(beta=0.5, window_size=2),
            functools.partial(sk_metrics.fbeta_score, beta=0.5),
            [True, False, True, True, True],
            [True, True, False, True, True]
        ),
        (
            metrics.RollingMicroFBeta(beta=0.5, window_size=2),
            functools.partial(sk_metrics.fbeta_score, beta=0.5, average='micro'),
            [0, 1, 0, 2, 2],
            [0, 0, 1, 1, 2]
        ),
        (
            metrics.RollingF1(3),
            sk_metrics.f1_score,
            [True, False, True, True, True],
            [True, True, False, True, True]
        )
    ]
)
def test_rolling_metric(metric, sk_metric, y_true, y_pred):

    def tail(iterable, n):
        return collections.deque(iterable, maxlen=n)

    n = metric.window_size

    for i, (yt, yp) in enumerate(zip(y_true, y_pred)):

        if isinstance(yp, list):
            yp = dict(enumerate(yp))

        metric.update(yt, yp)

        if i >= 1:
            assert math.isclose(
                metric.get(),
                sk_metric(tail(y_true[:i + 1], n), tail(y_pred[:i + 1], n))
            )


@pytest.mark.parametrize(
    'metric, sk_metric, y_true, y_pred',
    [
        (
            metrics.MultiF1(default_weight=2, weights={0: 1, 1: 1}),
            sk_metrics.f1_score,
            [0, 1, 2, 2, 2],
            [0, 1, 0, 2, 1]
        )
    ]
)
def test_MultiF1(metric, sk_metric, y_true, y_pred):

    for i, (yt, yp) in enumerate(zip(y_true, y_pred)):

        metric.update(yt, yp)

        if i >= 2:
            f1_0, f1_1, f1_2 = sk_metric(y_true[:i + 1], y_pred[:i + 1], average=None)
            multi_f1 = f1_0 * 1 + f1_1 * 1 + f1_2 * 2
            multi_f1 /= (1 + 1 + 2)
            assert math.isclose(metric.get(), multi_f1)


@pytest.mark.parametrize(
    'metric, sk_metric, y_true, y_pred',
    [
        (
            metrics.MultiFBeta(
                beta={0: 0.25, 1: 1},
                default_beta=4,
                default_weight=2,
                weights={0: 1, 1: 1}
            ),
            sk_metrics.fbeta_score,
            [0, 1, 2, 2, 2],
            [0, 1, 0, 2, 1]
        )
    ]
)
def test_MultiFBeta(metric, sk_metric, y_true, y_pred):

    for i, (yt, yp) in enumerate(zip(y_true, y_pred)):

        metric.update(yt, yp)

        if i >= 2:
            fbeta_0, _, _ = sk_metric(y_true[:i + 1], y_pred[:i + 1], beta=0.25, average=None)
            _, fbeta_1, _ = sk_metric(y_true[:i + 1], y_pred[:i + 1], beta=1, average=None)
            _, _, fbeta_2 = sk_metric(y_true[:i + 1], y_pred[:i + 1], beta=4, average=None)

            multi_fbeta = fbeta_0 * 1 + fbeta_1 * 1 + fbeta_2 * 2
            multi_fbeta /= (1 + 1 + 2)

            assert math.isclose(metric.get(), multi_fbeta)


@pytest.mark.parametrize(
    'metric, sk_metric, y_true, y_pred',
    [
        (
            metrics.RollingMultiF1(default_weight=2, weights={0: 1, 1: 1}, window_size=4),
            sk_metrics.f1_score,
            [0, 1, 2, 2, 0, 1],
            [0, 1, 0, 2, 1, 2]
        )
    ]
)
def test_RollingMultiF1(metric, sk_metric, y_true, y_pred):

    def tail(iterable, n):
        return collections.deque(iterable, maxlen=n)

    n = metric.window_size

    for i, (yt, yp) in enumerate(zip(y_true, y_pred)):

        metric.update(yt, yp)

        if i >= 2:
            sk_y_true, sk_y_pred = tail(y_true[:i + 1], n), tail(y_pred[:i + 1], n)
            f1_0, f1_1, f1_2 = sk_metric(sk_y_true, sk_y_pred, average=None)
            multi_fbeta = f1_0 * 1 + f1_1 * 1 + f1_2 * 2
            multi_fbeta /= (1 + 1 + 2)

            assert math.isclose(metric.get(), multi_fbeta)


@pytest.mark.parametrize(
    'metric, sk_metric, y_true, y_pred',
    [
        (
            metrics.RollingMultiFBeta(
                beta={0: 0.25, 1: 1},
                default_beta=4,
                default_weight=2,
                weights={0: 1, 1: 1},
                window_size=4
            ),
            sk_metrics.fbeta_score,
            [0, 1, 2, 2, 0, 1],
            [0, 1, 0, 2, 1, 2]
        )
    ]
)
def test_RollingMultiFBeta(metric, sk_metric, y_true, y_pred):

    def tail(iterable, n):
        return collections.deque(iterable, maxlen=n)

    n = metric.window_size

    for i, (yt, yp) in enumerate(zip(y_true, y_pred)):

        metric.update(yt, yp)

        if i >= 2:
            sk_y_true, sk_y_pred = tail(y_true[:i + 1], n), tail(y_pred[:i + 1], n)
            fbeta_0, _, _ = sk_metric(sk_y_true, sk_y_pred, beta=0.25, average=None)
            _, fbeta_1, _ = sk_metric(sk_y_true, sk_y_pred, beta=1, average=None)
            _, _, fbeta_2 = sk_metric(sk_y_true, sk_y_pred, beta=4, average=None)

            multi_fbeta = fbeta_0 * 1 + fbeta_1 * 1 + fbeta_2 * 2
            multi_fbeta /= (1 + 1 + 2)

            assert math.isclose(metric.get(), multi_fbeta)
