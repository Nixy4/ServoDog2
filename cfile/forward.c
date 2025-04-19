#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define PI 3.14159265358979323846

typedef struct {
    double AS1, AS2, RS1, RS2;
    double L6, L7, R12, R13, R17, R35, R7X;
    double X, Z;
} KinematicsData;

double L1 = 80.0, L2 = 65.0, L3 = 20.0, L4 = 32.0, L8 = 15.0, L9 = 73.0;
double _L1 = 75.0, L1_ = 5.0;
double L5 = sqrt(pow(_L1, 2) + pow(L4, 2));
double R14 = PI / 2;
double R15 = atan(L4 / _L1);

double F1_RS2_to_L6(double RS2) {
    double _a = 1;
    double _b = -2 * L8 * cos(RS2);
    double _c = pow(L8, 2) - pow(L9, 2);
    double D = pow(_b, 2) - 4 * _a * _c;
    if (D < 0) {
        fprintf(stderr, "Error: Discriminant is negative.\n");
        return 0;
    }
    return (-_b + sqrt(D)) / (2 * _a);
}

double F2_L6_to_R35(double L6) {
    double T = (pow(L3, 2) + pow(L5, 2) - pow(L6, 2)) / (2 * L3 * L5);
    return acos(T);
}

double F3_R15R35_to_R13(double R15, double R35) {
    return R15 + R35;
}

double F4_R13_to_R12(double R13) {
    return PI - R13;
}

double F5_R12_to_L7(double R12) {
    return sqrt(pow(L1, 2) + pow(L2, 2) - 2 * L1 * L2 * cos(R12));
}

double F6_L7_to_R17(double L7) {
    double T = (pow(L1, 2) + pow(L7, 2) - pow(L2, 2)) / (2 * L1 * L7);
    return acos(T);
}

double F7_RS1R17_to_R7X(double RS1, double R17) {
    return RS1 + R17;
}

void F8_L7R7X_to_xz(double L7, double R7X, double *X, double *Z) {
    *X = L7 * cos(R7X);
    *Z = L7 * sin(R7X);

    if (R7X > PI / 2) {
        *X = -*X;
    } else if (R7X > PI) {
        *X = -*X;
        *Z = -*Z;
    }
}

KinematicsData caculateFromAngles(double AS1, double AS2) {
    KinematicsData data = {0};
    if (AS2 > 120) {
        fprintf(stderr, "Error: AS2 > 120\n");
        AS2 = 120;
    }

    data.AS1 = AS1;
    data.AS2 = AS2;
    data.RS1 = AS1 * PI / 180;
    data.RS2 = AS2 * PI / 180;

    data.L6 = F1_RS2_to_L6(data.RS2);
    data.R35 = F2_L6_to_R35(data.L6);
    data.R13 = F3_R15R35_to_R13(R15, data.R35);
    data.R12 = F4_R13_to_R12(data.R13);
    data.L7 = F5_R12_to_L7(data.R12);
    data.R17 = F6_L7_to_R17(data.L7);
    data.R7X = F7_RS1R17_to_R7X(data.RS1, data.R17);
    F8_L7R7X_to_xz(data.L7, data.R7X, &data.X, &data.Z);

    if (data.RS1 + data.R17 > PI / 2) {
        data.X = -data.X;
    }

    return data;
}

void caculateAllAngle() {
    KinematicsData *datas = malloc(181 * 121 * sizeof(KinematicsData));
    double *x_values = malloc(181 * 121 * sizeof(double));
    double *z_values = malloc(181 * 121 * sizeof(double));
    KinematicsData x_min, x_max, z_min, z_max, start, end;

    int index = 0;
    for (int AS1 = 0; AS1 <= 180; AS1++) {
        for (int AS2 = 0; AS2 <= 120; AS2++) {
            KinematicsData data = caculateFromAngles(AS1, AS2);
            datas[index] = data;
            x_values[index] = data.X;
            z_values[index] = data.Z;
            index++;
        }
    }

    x_min = datas[0];
    x_max = datas[0];
    z_min = datas[0];
    z_max = datas[0];
    start = datas[0];
    end = datas[index - 1];

    for (int i = 1; i < index; i++) {
        if (datas[i].X < x_min.X) x_min = datas[i];
        if (datas[i].X > x_max.X) x_max = datas[i];
        if (datas[i].Z < z_min.Z) z_min = datas[i];
        if (datas[i].Z > z_max.Z) z_max = datas[i];
    }

    printf("X最小值元素: X=%.2f, Z=%.2f\n", x_min.X, x_min.Z);
    printf("X最大值元素: X=%.2f, Z=%.2f\n", x_max.X, x_max.Z);
    printf("Z最小值元素: X=%.2f, Z=%.2f\n", z_min.X, z_min.Z);
    printf("Z最大值元素: X=%.2f, Z=%.2f\n", z_max.X, z_max.Z);
    printf("起始元素: X=%.2f, Z=%.2f\n", start.X, start.Z);
    printf("结束元素: X=%.2f, Z=%.2f\n", end.X, end.Z);

    free(datas);
    free(x_values);
    free(z_values);
}

int main() {
    caculateAllAngle();
    return 0;
}
