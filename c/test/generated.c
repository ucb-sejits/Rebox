// <file: generated.c>
#include <omp.h>
#include <stdio.h>
#include <stdint.h>
#include "aux.c"
void apply(double* arr, double* out) {
    #pragma omp parallel for
    for (size_t index = 0lu; index < 1073741824u; index ++) {
        
        long total = 0;

        
        size_t delta;
        
        total += arr[clamp(add(index, 18446744073709551615lu))] * 1l;

        
        total += arr[clamp(add(index, 13176245766935394011lu))] * 1l;

        
        total += arr[clamp(add(index, 13176245766935394015lu))] * 1l;

        
        total += arr[clamp(add(index, 15811494920322472813lu))] * 1l;

        
        total += arr[clamp(add(index, 10540996613548315209lu))] * 1l;

        
        total += arr[clamp(add(index, 10540996613548315213lu))] * 1l;

        
        total += arr[clamp(add(index, 15811494920322472815lu))] * 1l;

        
        total += arr[clamp(add(index, 10540996613548315211lu))] * 1l;

        
        total += arr[clamp(add(index, 10540996613548315215lu))] * 1l;

        
        total += arr[clamp(add(index, 7905747460161236406lu))] * 1l;

        
        total += arr[clamp(add(index, 2635249153387078802lu))] * 1l;

        
        total += arr[clamp(add(index, 2635249153387078806lu))] * 1l;

        
        total += arr[clamp(add(index, 5270498306774157604lu))] * 1l;

        
        total += arr[clamp(add(index, 0lu))] * 1l;

        
        total += arr[clamp(add(index, 4lu))] * 1l;

        
        total += arr[clamp(add(index, 5270498306774157606lu))] * 1l;

        
        total += arr[clamp(add(index, 2lu))] * 1l;

        
        total += arr[clamp(add(index, 6lu))] * 1l;

        
        total += arr[clamp(add(index, 7905747460161236407lu))] * 1l;

        
        total += arr[clamp(add(index, 2635249153387078803lu))] * 1l;

        
        total += arr[clamp(add(index, 2635249153387078807lu))] * 1l;

        
        total += arr[clamp(add(index, 5270498306774157605lu))] * 1l;

        
        total += arr[clamp(add(index, 1lu))] * 1l;

        
        total += arr[clamp(add(index, 5lu))] * 1l;

        
        total += arr[clamp(add(index, 5270498306774157607lu))] * 1l;

        
        total += arr[clamp(add(index, 3lu))] * 1l;

        
        total += arr[clamp(add(index, 7lu))] * 1l;


        
        out[index] = total;

    };
};
