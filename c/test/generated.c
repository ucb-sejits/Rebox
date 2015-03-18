// <file: generated.c>
#include <omp.h>
#include <stdio.h>
#include <stdint.h>
#include "aux.c"
void apply(long* arr, long* out) {
    double s = omp_get_wtime();
    #pragma omp parallel for
    for (size_t index = 0lu; index < 1073741824u; index ++) {
        
        long total;
        long neg = 0;

        

        neg += arr[clamp(add(index, 10540996613548315209lu))];
        __builtin_prefetch(&arr[index]);
        
        neg += arr[clamp(add(index, 2635249153387078802lu))];
        
        neg += arr[clamp(add(index, 5270498306774157604lu))];

        total = arr[index] * 4l;
        
        neg += arr[clamp(add(index, 4lu))];
        
        neg += arr[clamp(add(index, 2lu))];
        
        neg += arr[clamp(add(index, 1lu))];
        
        neg += arr[clamp(add(index, 3lu))];


        
        out[index] = arr[index]*4 + neg * -1l;

    };
    double e = omp_get_wtime();
    printf("Time:%f\n", e - s);
};
