from LinearRegressor import LinearRegressor
from Utilities import distance_from_point_to_line
import matplotlib.pyplot as plt
import random
import math
import time


class RANSAC:
    def __init__(
        self,
        sample_count=500,
        default_sample_size=2,
        inlier_distance_threshold=40,
        score_threshold=1,
        sample: callable = None,
        score_model: callable = None,
        compare: callable = None,
    ):
        self.default_sample_size = default_sample_size  # `sample_points`: Minimum number of data points to estimate parameters
        self.sample_count = sample_count  # `sample_count`: Maximum iterations allowed
        self.score_threshold = score_threshold  # `score_threshold`: Threshold value to determine if points are fit well
        self.inlier_distance_threshold = inlier_distance_threshold  # `inlier_distance_threshold`: Maximum distance from the line to consider a point an inlier

        if sample is not None:
            self.sample = sample
        else:
            self.sample = self._sample

        if score_model is not None:
            self.score_model = score_model
        else:
            self.score_model = self._score_model

        if compare is not None:
            self.compare = compare
        else:
            self.compare = self._compare

        self.best_model = None
        self.best_inliers = set()
        self.best_error = math.inf
        self.point_list = []

    def fit(self, point_list):
        self.point_list = point_list
        sample_number = 0

        while sample_number < self.sample_count:
            sample_points = self.sample(self, point_list, self.default_sample_size)
            sample_model = LinearRegressor().smart_fit(sample_points)
            inliers = set()

            for point in self.point_list:
                distance = distance_from_point_to_line(
                    point,
                    sample_model.slope,
                    sample_model.x_intercept,
                    sample_model.y_intercept,
                )
                if distance < self.inlier_distance_threshold:
                    inliers.add((point[0], point[1]))

            if self.score_model(self, sample_model, inliers) >= self.score_threshold:
                # Found an acceptable model
                # print("Found a good model")
                # print(f"Inlier count: {len(inliers)}")
                # print(f"Inliers: {inliers}")
                # print(f"Sample points: {sample_points}")
                refined_model = LinearRegressor().smart_fit(inliers)

                for point in self.point_list:
                    distance = distance_from_point_to_line(
                        point,
                        refined_model.slope,
                        refined_model.x_intercept,
                        refined_model.y_intercept,
                    )
                    if distance < self.inlier_distance_threshold:
                        inliers.add((point[0], point[1]))

                refined_model_error = self._model_error(self, refined_model, inliers)

                if self.compare(
                    self,
                    refined_model,
                    refined_model_error,
                    inliers,
                    self.best_model,
                    self.best_error,
                    self.best_inliers,
                ):
                    # print(f"Inliers: {len(self.best_inliers)} -> {len(inliers)}")
                    # print(f"Error: {self.best_error} -> {refined_model_error}")
                    self.best_error = refined_model_error
                    self.best_model = refined_model
                    self.best_inliers = inliers
                    # print(f"Found new best model: {self.best_model.slope, self.best_model.x_intercept, self.best_model.y_intercept}")

            sample_number += 1

        if self.best_model:
            print(
                f"Returning best model: {self.best_model.slope, self.best_model.x_intercept, self.best_model.y_intercept}"
            )
        return self.best_model, self.best_inliers

    @staticmethod
    def _sample(self, point_list, default_sample_points):
        return random.sample(point_list, default_sample_points)

    @staticmethod
    def _score_model(self, model, inliers):
        return len(inliers)

    @staticmethod
    def _model_error(self, model, inliers):
        sum_distance_errors = sum(
            [
                distance_from_point_to_line(
                    point[:2], model.slope, model.x_intercept, model.y_intercept
                )
                ** 2
                for point in inliers
            ]
        )
        return math.sqrt(sum_distance_errors) / len(inliers)

    @staticmethod
    def _compare(
        self,
        model,
        model_error,
        model_inliers,
        reference_model,
        reference_error,
        reference_model_inliers,
    ):
        return all(
            (
                model_error <= reference_error,
                len(model_inliers) >= len(reference_model_inliers),
            )
        )


def sample(self, point_list, default_sample_points):
    return random.sample(point_list, default_sample_points)


def score_model(self, model, inliers):
    horizontal_vertical_threshold = 20
    if not (
        -1 / horizontal_vertical_threshold
        <= model.slope
        <= 1 / horizontal_vertical_threshold
        or -horizontal_vertical_threshold >= model.slope
        or model.slope >= horizontal_vertical_threshold
    ):
        return 0
    return len(inliers)


def compare(
    self,
    model,
    model_error,
    model_inliers,
    reference_model,
    reference_error,
    reference_model_inliers,
):
    global optimal_model, optimal_model_position_error
    if reference_model is None:
        return model

    reference_model_matches_optimal = False
    new_model_matches_optimal = False

    if reference_model.slope > 1:
        y_list = [44, 712 + 44]
        x_list = reference_model.predict_x(y_list)
        for x in x_list:
            if abs(x - optimal_model.x_intercept) < optimal_model_position_error:
                reference_model_matches_optimal = True
                print("Reference model matches optimal model")

    if model.slope > 1:
        y_list = [44, 712 + 44]
        x_list = model.predict_x(y_list)
        for x in x_list:
            if abs(x - optimal_model.x_intercept) < optimal_model_position_error:
                new_model_matches_optimal = True
                print("New model matches optimal model")

    if not any((reference_model_matches_optimal, new_model_matches_optimal)):
        # Neither model matches optimal, compare using other metrics
        return model_error <= reference_error and len(model_inliers) >= len(
            reference_model_inliers
        )
    elif not reference_model_matches_optimal:
        # Reference model does not match optimal, use new model
        return model
    elif not new_model_matches_optimal:
        # The reference model matches optimal, new model does not; use the reference model
        return reference_model
    else:
        # Both models matched the optimal model, compare using other metrics
        return model_error <= reference_error and len(model_inliers) >= len(
            reference_model_inliers
        )


if __name__ == "__main__":

    # Point list with only obstacles and vertical lines
    point_list = [(356.0, 588.35), (359.70928298318654, 592.1208667605497), (470.2991629246891, 620.1297812718478), (473.32274363831937, 615.8410741687717), (473.72797411774053, 606.1846800068499), (476.3123644763457, 601.5880912811327), (481.4716243655176, 602.2519281225607), (488.79848128714934, 606.8126858191685), (491.2041686366442, 601.9354697543063), (492.8085248208996, 595.8508769242474), (498.20071948986623, 596.4482852435515), (499.59566804805957, 590.3268331686114), (501.83865792341055, 585.8049531235142), (511.1538483662756, 592.1991603226784), (508.170022469017, 579.911388470479), (516.2539637444631, 584.0183262463557), (515.7159476791694, 575.8301427965284), (521.956150280073, 577.0328396058297), (528.87043448282, 578.8632212405606), (525.9722161248636, 568.1600062349274), (536.5344094965731, 574.2286131851732), (540.784205951147, 572.3545073623503), (543.3165858529212, 568.4689604728237), (548.1618979198777, 567.1831683937669), (545.7735714410803, 558.0883277369002), (552.3343977386103, 558.6013817564431), (557.0304578913372, 557.0304578913368), (559.7503838328645, 553.4478582131578), (566.2527763640202, 553.4404990274813), (568.5145043647285, 549.3733204441949), (570.5130131375669, 545.1186606859277), (571.6131115458907, 540.150994104025), (581.933745612931, 542.9086493940595), (587.5341910971019, 541.4938650683973), (588.9179437730411, 536.6696767405534), (591.1272817116652, 532.5385567514415), (592.3138640569184, 527.6920721946284), (597.0269067534144, 525.3965472519513), (598.6654404921542, 520.9152630618132), (709.3166668344107, 588.0856707382654), (718.9765751733253, 586.3519391614759), (703.5361309907246, 568.9704149782183), (717.8559481524641, 570.0010111814594), (716.4603627039947, 561.6029609327416), (708.647715716646, 549.8697223003793), (586.4197939048726, 478.00100082308677), (588.396776671426, 474.41207209456456), (592.315956561405, 471.76999254758346), (704.9691734598225, 520.2124282743548), (715.0017506667136, 518.0955058545576), (710.1385661858035, 509.2494422986948), (710.8621284375787, 502.9887063714283), (717.7760306591193, 499.2372634496085), (717.5491179157492, 492.61802712068504), (717.0159510477395, 485.9737399981196), (707.9674056178146, 476.5053775051657), (716.0224442435194, 472.97838322063296), (702.4271782136551, 462.5749158804489), (712.1969353597169, 459.48477600760043), (707.7258626406415, 452.22130766987505), (709.266493442643, 446.70341909620277), (708.9945903523661, 440.74650321379033), (718.0163228411695, 436.9202353960459), (707.8592364266663, 428.86654490397933), (703.4841149452614, 422.2861400346982), (712.6342038011794, 418.24263252865325), (715.9877079384081, 413.0164516455379), (702.2607742863556, 405.2802058701686), (711.3754860108454, 400.89436426273426), (704.7312012214618, 394.5002830462951), (698.9710968057678, 388.4203139382294), (695.5251209361539, 382.72120652751096), (695.3789890020336, 377.35191616594363), (696.1969191651654, 372.0432794504369), (698.5558859013408, 366.7652524050521), (692.433489914275, 361.28511959249573), (694.925, 356.0000000000008), (686.55, 356.0), (696.9079378446304, 350.64459016253466), (685.5872882805955, 345.64230219398735), (687.5565217467445, 340.36419134820227), (681.0822561172986, 335.5475580263144), (687.8987033330959, 329.8790055548077), (687.1487984761042, 324.6972222824288), (678.6645751646461, 320.3774992620685), (676.7506829349688, 315.4797655886607), (680.4307526337075, 309.82666629405537), (677.1962483615347, 305.1275119689176), (670.4468969086016, 301.1202311908129), (709.647967443584, 288.53804221627684), (714.3710681173012, 281.7849195819003), (718.4066895459453, 274.99250730739595), (719.0100005324623, 268.8490095384942), (705.0289421127054, 266.3845991601438), (705.5556084491116, 260.3724066925473), (707.7075623791771, 253.81950741313327), (717.7915509265385, 244.69838589144192), (705.9174687578839, 242.30492234460093), (711.1840958378278, 234.3933032729609), (714.1697867216524, 227.0509422106228), (707.2826196773906, 223.2613592897927), (713.8012361819481, 214.33646901311812), (711.0007103674566, 208.9538911137164), (717.1823329379295, 199.70244764068264), (702.60666610447, 199.50108942247246), (714.4924781870291, 187.30624468192187), (593.8650541295921, 239.471112384415), (593.4086883699905, 235.0342313443977), (591.8549525299179, 231.12123081921055), (707.5304246995922, 162.7445136340988), (703.2788794723924, 157.91562436072138), (717.5116513416624, 142.2026053848403), (714.0236050122794, 136.6028526757753), (714.7971519420871, 128.3004034736716), (717.1523608472385, 118.7672403430013), (704.2422757983009, 119.3347937553626), (710.8928936760428, 106.57709679492424), (702.3604007167675, 104.35443886228975), (711.5597912798189, 89.0381573144814), (702.9965736847755, 86.84186738830192), (607.6692956064305, 154.37487439814106), (606.6094322128268, 148.67784733423727), (598.6645537721128, 148.74489157662757), (588.309398264549, 151.19171530926872), (590.0932415607285, 142.99153947415783), (580.1214045007122, 145.53599228222518), (579.7322480681254, 139.18836822166048), (568.2381003731437, 143.76189962685595), (565.6611277933508, 139.64649964139363), (567.5592830872605, 130.7122456954133), (560.5116775427839, 131.2446010133731), (552.1781648482602, 133.47955119412526), (549.844006225351, 129.0378294175311), (550.5896084705311, 120.78156981162087), (538.6959041812947, 127.95823497573767), (535.4591853095914, 124.64261237639758), (537.4169710822144, 114.37528043812702), (529.5142064767373, 117.17818326051622), (524.2177864852621, 116.65030016730768), (523.1776486576688, 110.00556019638984), (519.4440929180446, 107.18014852066418), (512.6087765024878, 109.22405557389564), (506.44039924583865, 110.50358067834912), (503.08751708106706, 107.28859129721471), (497.577314504561, 107.78854474928553), (494.8654965598172, 103.40459947736008), (493.87551977187866, 95.5984570943649), (488.58792544893186, 95.78154461079237), (480.94272423907967, 100.96016848398543), (359.73323664208755, 118.35432137491952), (356.00000000000057, 123.9), (356.00000000000006, 118.875), (352.32841457836196, 122.27883715741004), (3.160960112352143, 24.662087052867662), (3.8431449033074614, 35.56191700515768), (9.617460821395014, 50.62271339017133), (3.3997537512656777, 54.850939989294034), (-2.577600356784444, 59.358810770702405), (0.02618045280280512, 70.81119337887577), (-1.3476043469063939, 78.81278498544157), (-1.159160596794095, 87.83731686382953), (-6.035104982787061, 92.96609959912007), (5.750105970347477, 109.84025160027281), (9.432562364601495, 120.47301259551111), (9.996647577570513, 128.7182789192238), (-1.0662796948033701, 129.3988484033822), (-5.62600970668035, 134.39529623984774), (2.428693857457233, 146.89851244514307), (-1.8761839485349014, 151.87102860584807), (4.44766763340516, 162.73246979224598), (121.36022521145026, 231.76463431381688), (122.53401549954734, 237.04313930574773), (117.25936898404069, 239.04217169380507), (-1.9948233081814806, 187.54042329227886), (2.967940795260006, 196.59991319431083), (-4.218690580961265, 200.11945292584932), (6.35779092110397, 211.1734550214317), (7.728972798410325, 218.10974567813764), (-3.3274383425234078, 220.2214756332923), (0.5587675083153272, 228.03328217933426), (-4.978868660648686, 232.40930908649614), (2.7776098479836833, 241.23108828914567), (-3.4259632149087906, 245.42613569639263), (3.788283435836945, 253.6730370824609), (-5.37143682521031, 257.13996183047357), (-2.714773723987321, 263.89770028849614), (0.3313923665363063, 270.61152203560476), (-2.405430822003268, 275.88689459711986), (-1.391845306679329, 281.98770687725613), (6.281181559319748, 289.2875674746173), (1.6315476489764933, 294.15280440198916), (4.778026084372243, 300.37190423169403), (0.5567562883126698, 305.41293520360864), (4.940212939868729, 311.65083530327007), (-3.59022465979848, 316.3008696050362), (-0.2369599840982346, 322.325692786802), (8.225388127198869, 328.62954445534046), (4.869246270723579, 333.90872546659875), (4.815292210246525, 339.43854959175655), (4.773394687481357, 344.9622592599451), (-0.6559948062098897, 350.39719991487254), (-5.550000000000011, 355.9999999999993), (5.5, 356.0), (-4.455526009640209, 361.6624878909114), (-5.196683252166906, 367.35106306185867), (-5.348412267491597, 373.0407585442132), (1.4011033894352636, 378.30947158876506), (6.829703859972426, 383.48029827867765), (3.2475068920142576, 389.34492811658254), (1.9014096190933856, 395.09284832618476), (4.716987132075246, 400.3773646742811), (0.309250373883458, 406.6222901043751), (1.4939623518933445, 412.1482403645644), (5.645868153056881, 417.1465845143716), (6.600424915806514, 422.65153359814207), (0.4686780335019307, 429.62699726156586), (-6.431087465000644, 437.0129462736406), (9.447360370268825, 439.19992767824453), (-4.555081730132031, 448.57481049711697), (-6.601247533744129, 455.19647630823187), (-6.678917738041889, 461.3679659733666), (0.5166829711344008, 465.36094796202366), (-4.3553140242295285, 473.08653916866626), (7.533110209845518, 475.30688305783303), (4.557510776370009, 482.52708165962355), (-1.4331641800939678, 491.06273780805486), (4.939643340746727, 494.99462797991606), (1.9693631416765243, 502.6442912823018), (8.859312835036917, 506.22118963260465), (-2.887825257124234, 518.0440665597276), (1.8959330174242268, 522.6287257539908), (118.47170621131752, 472.3639104268895), (124.31602854791913, 474.048879694776), (122.84053264184885, 479.45158324729675), (-0.9854337828642201, 552.2544029871838), (-6.175909945006367, 562.5814918028939), (-2.8433510579407084, 568.219366226328), (-0.9364888027320148, 574.7309616542144), (-2.670502753259825, 583.6192225070804), (-1.0360095924898474, 590.5288222783515), (1.1617566218594675, 597.1478211830083), (-4.374496782790175, 609.2754383937654), (5.958571958817572, 610.3199840356475), (0.940011631729817, 622.5865800446943), (9.1417034423813, 625.0508738773157), (-2.1980462081094743, 642.9707481916803), (-1.3062535061989138, 651.5894396462082), (2.031023013183983, 658.3180664977021), (6.654522096352821, 663.9894684778594), (8.16998680893272, 672.5009597908105), (-2.7619099854464935, 692.8998581828034), (3.5256599003805604, 697.5713983874255), (352.3036755535952, 591.2959685387523), (355.9999999999995, 592.725)]

    optimal_model = LinearRegressor()
    optimal_model.slope = math.inf
    optimal_model.x_intercept = 712 + 44

    optimal_model_position_error = 20

    while True:
        start_time = time.perf_counter()

        ransac = RANSAC(
            150, 2, 12, 20, sample=sample, score_model=score_model, compare=compare
        )

        model, inliers = ransac.fit(point_list)

        print(
            f"Linear Regression took: {round((time.perf_counter() - start_time) * 1000)} ms"
        )

        if not model:
            print("Couldn't find any lines")
            break

        fig, ax = plt.subplots()

        x_data = [point[0] for point in point_list]
        y_data = [point[1] for point in point_list]

        plt.scatter(x_data, y_data)
        plt.scatter(
            [point[0] for point in inliers],
            [point[1] for point in inliers],
            color="#11aa00",
        )

        x_data_inliers = [point[0] for point in inliers]
        y_data_inliers = [point[1] for point in inliers]

        x_limit = [min(x_data) - 25, max(x_data) + 25]
        y_limit = [min(y_data) - 25, max(y_data) + 25]
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit)
        if math.isinf(model.slope):
            x_values = [model.x_intercept, model.x_intercept]
            y_values = y_limit
        else:
            x_values = x_limit
            y_values = model.predict_y(x_values)
        plt.plot(x_values, y_values, c="peru")
        plt.show()

        for point in inliers:
            point_list.remove(point)
