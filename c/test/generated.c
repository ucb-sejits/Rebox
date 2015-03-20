// <file: generated.c>
#include <omp.h>
#include <stdio.h>
#include <stdint.h>
#include "aux.c"
void apply(double* arr, double* out) {
    #pragma omp parallel for
    for (size_t index = 0lu; index < 1073741824u; index ++) {
        
        double total = 0;
        uint64_t pf = clamp(add(index, 10540996613548315209lu));
        
        size_t delta;
        total += arr[clamp(add(index, 18446744073709551615lu))];

        
        total += arr[clamp(add(index, 13176245766935394011lu))];

        
        total += arr[clamp(add(index, 13176245766935394015lu))];

        
        total += arr[clamp(add(index, 15811494920322472813lu))];

        
        total += arr[pf];

        
        total += arr[clamp(add(index, 10540996613548315213lu))];

        
        total += arr[clamp(add(index, 15811494920322472815lu))];

        
        total += arr[clamp(add(index, 10540996613548315211lu))];

        
        total += arr[clamp(add(index, 10540996613548315215lu))];

        
        total += arr[clamp(add(index, 7905747460161236406lu))];

        
        total += arr[clamp(add(index, 2635249153387078802lu))];

        
        total += arr[clamp(add(index, 2635249153387078806lu))];

        
        total += arr[clamp(add(index, 5270498306774157604lu))];

        
        total += arr[index];

        
        total += arr[clamp(add(index, 4lu))];

        
        total += arr[clamp(add(index, 5270498306774157606lu))];

        
        total += arr[clamp(add(index, 2lu))];

        
        total += arr[clamp(add(index, 6lu))];

        
        total += arr[clamp(add(index, 7905747460161236407lu))];

        
        total += arr[clamp(add(index, 2635249153387078803lu))];

        
        total += arr[clamp(add(index, 2635249153387078807lu))];

        
        total += arr[clamp(add(index, 5270498306774157605lu))];

        
        total += arr[clamp(add(index, 1lu))];

        __builtin_prefetch(&arr[pf]);
        
        total += arr[clamp(add(index, 5lu))];

        
        total += arr[clamp(add(index, 5270498306774157607lu))];

        
        total += arr[clamp(add(index, 3lu))];

        
        total += arr[clamp(add(index, 7lu))];

        
        out[index] = total;

    };
};
