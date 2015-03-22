// <file: generated.c>
#include <omp.h>
#include <stdio.h>
#include <stdint.h>
#include <sched.h>
#include "aux.c"

#ifndef num_teams
#define num_teams 2
#endif

void apply(float* arr, float* out) {
	const uint64_t size = 1 << 30;
	const uint64_t block_size = (size / num_teams);
	const uint64_t threads = omp_get_max_threads();
	const uint64_t team_split = threads / num_teams;
	omp_set_dynamic(0);
	#pragma omp parallel num_threads(threads)
	{
#ifdef __linux__
		const uint64_t team_id = sched_getcpu() / team_split;
#else
		const uint64_t team_id = omp_get_thread_num() / team_split;
#endif
		const uint64_t start = block_size * team_id;
		const uint64_t end = start + block_size;
#ifdef __linux__
#ifdef VERBOSE
		printf("CPU: %d\tteam: %d\tID: %d\tStart: %d\tEnd: %d\n", sched_getcpu(), team_id, omp_get_thread_num(), start, end);
#endif
#endif
		for (uint64_t index = start + (omp_get_thread_num() % team_split); index < end; index += team_split) {
			float total = 0;
			total += arr[clamp(add(index, 18446744073709551615lu))];


			total += arr[clamp(add(index, 13176245766935394011lu))];


			total += arr[clamp(add(index, 13176245766935394015lu))];


			total += arr[clamp(add(index, 15811494920322472813lu))];


			total += arr[clamp(add(index, 10540996613548315209lu))];



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


			total += arr[clamp(add(index, 5lu))];


			total += arr[clamp(add(index, 5270498306774157607lu))];


			total += arr[clamp(add(index, 3lu))];


			total += arr[clamp(add(index, 7lu))];


			out[index] = total;
		};
	}
};
