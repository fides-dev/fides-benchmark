import petab
import pandas as pd
import re


def fix_fiedler(petab_problem):
    petab_problem.parameter_df = petab_problem.parameter_df.append(
        pd.Series({
            petab.PARAMETER_NAME: 'sigma_{pErk}',
            petab.PARAMETER_SCALE: petab.LOG10,
            petab.LOWER_BOUND: 1e-5,
            petab.UPPER_BOUND: 1e3,
            petab.NOMINAL_VALUE: 0.04527013133744955,
            petab.ESTIMATE: 1.0
        }, name='sigma_pErk'))
    petab_problem.parameter_df = petab_problem.parameter_df.append(
        pd.Series({
            petab.PARAMETER_NAME: 'sigma_{pMek}',
            petab.PARAMETER_SCALE: petab.LOG10,
            petab.LOWER_BOUND: 1e-5,
            petab.UPPER_BOUND: 1e3,
            petab.NOMINAL_VALUE: 0.0005804511382145272,
            petab.ESTIMATE: 1.0
        }, name='sigma_pMek'))
    petab_problem.parameter_df.drop(index=[
        'pErk_20140430_gel1_sigma',
        'pMek_20140430_gel1_sigma',
        'pErk_20140505_gel1_sigma',
        'pMek_20140505_gel1_sigma',
        'pErk_20140430_gel2_sigma',
        'pMek_20140430_gel2_sigma',
        'pErk_20140505_gel2_sigma',
        'pMek_20140505_gel2_sigma',
    ], inplace=True)
    new_measurement_dfs = []
    new_observable_dfs = []
    for (obs_id, noise_par, obs_par), measurements in \
            petab_problem.measurement_df.groupby([
                petab.OBSERVABLE_ID, petab.NOISE_PARAMETERS,
                petab.OBSERVABLE_PARAMETERS
            ]):
        replacement_id = f'{obs_id}_{obs_par[-4:]}'

        measurements.drop(columns=[petab.NOISE_PARAMETERS,
                                   petab.OBSERVABLE_PARAMETERS],
                          inplace=True)
        measurements[petab.OBSERVABLE_ID] = replacement_id

        observable = petab_problem.observable_df.loc[obs_id].copy()
        observable.name = replacement_id
        for target in [petab.OBSERVABLE_FORMULA,
                       petab.NOISE_FORMULA]:
            observable[target] = re.sub(
                fr'observableParameter[0-9]+_{obs_id}',
                obs_par,
                observable[petab.OBSERVABLE_FORMULA]
            )
        observable[petab.NOISE_FORMULA] = re.sub(
            r'^pERK',
            r'sigma_pErk',
            observable[petab.OBSERVABLE_FORMULA]
        )
        observable[petab.NOISE_FORMULA] = re.sub(
            r'^pMEK',
            r'sigma_pMek',
            observable[petab.NOISE_FORMULA]
        )
        new_measurement_dfs.append(measurements)
        new_observable_dfs.append(observable)

    petab_problem.observable_df = pd.concat(new_observable_dfs, axis=1).T
    petab_problem.observable_df.index.name = petab.OBSERVABLE_ID
    petab_problem.measurement_df = pd.concat(new_measurement_dfs)
