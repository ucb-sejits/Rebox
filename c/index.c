#include <stdio.h>
#include <time.h>

#define DIM 512
#define REPEAT 3

unsigned long z_order(int x, int y, int z, int xlen, int ylen, int zlen) //x, y, z are 12 bit numbers
{
	unsigned long output = 0;
	for (int offset = 0; offset < 12; offset++)
	{
		output |= (x & (1 << offset)) << (3 * offset);
		output |= (y & (1 << offset)) << (3 * offset + 1);
		output |= (z & (1 << offset)) << (3 * offset + 2);
	}
	return output;
}

unsigned long standard_order(int x, int y, int z, int xlen, int ylen, int zlen)
{
	unsigned long output = 0;
	output += x;
	output *= ylen;
	output += y;
	output *= zlen;
	output += z;
	return output;
}

int kernel(int* region) // calculates 27 pt average stencil
{
	int total = 0;
	for (int i = 0; i < 9; i++)
	{
		total += region[i];
	}
	return total/9;
}

int main(int argc, char** argv)
{
	printf("allocating\n");
	long size = DIM*DIM*DIM;
	int stdmatrix[size];
	int zmatrix[size];
	int stdoutmatrix[size];
	int zoutmatrix[size];
	int neighborhood[27];
	long min_loc;
	long max_loc;
	long location;
	int std_total_distance = 0;
	int z_total_distance = 0;
	printf("Allocated\n");
	for (int i = 0; i < DIM; i++)
	{
		for (int j = 0; j < DIM; j++)
		{
			for (int k = 0; k < DIM; k++)
			{
				stdmatrix[standard_order(i, j, k, 3, 3, 3)] = i + j + k;
				zmatrix[z_order(i, j, k, 3, 3, 3)] = i + j + k;
			}
		}
	}
	for (int count = 0; count < REPEAT; count++)
	{
		printf("Repeat: %d\n", count);
		float startTime = (float)clock()/CLOCKS_PER_SEC;
		//leaving edges untouched
		for (int i = 1; i < DIM - 1; i++)
		{
			for (int j = 1; j < DIM - 1; j++)
			{
				for (int k = 1; k < DIM - 1; k++)
				{
					min_loc = size;
					max_loc = 0;
					for (int dx = -1; dx <= 1; dx++)
					{
						for (int dy = -1; dy <= 1; dy++)
						{
							for (int dz = -1; dz <= 1; dz++)
							{
								location = standard_order(i+dx, j+dy, k+dz, 3, 3, 3);
								if (location < min_loc){
									min_loc = location;
								}
								if (location > max_loc)
								{
									max_loc = location;
								}
								neighborhood[9*(dx+1)+3*(dy+1)+dz+1] = stdmatrix[location];
							}
						}
					}
					stdoutmatrix[standard_order(i, j, k, 3, 3, 3)] = kernel(neighborhood);
					std_total_distance += (int) (max_loc - min_loc);
				}
			}
		}

		float midTime = (float)clock()/CLOCKS_PER_SEC;
		printf("Finished Regular in time %f\n", midTime-startTime);
		for (int i = 1; i < DIM - 1; i++)
		{
			for (int j = 1; j < DIM - 1; j++)
			{
				for (int k = 1; k < DIM - 1; k++)
				{
					max_loc = 0;
					min_loc = size;
					for (int dx = -1; dx <= 1; dx++)
					{
						for (int dy = -1; dy <= 1; dy++)
						{
							for (int dz = -1; dz <= 1; dz++)
							{
								location = z_order(i+dx, j+dy, k+dz, 3, 3, 3);
									if (location < min_loc){
										min_loc = location;
									}
									if (location > max_loc)
									{
										max_loc = location;
									}
								neighborhood[9*(dx+1)+3*(dy+1)+dz+1] = zmatrix[location];
							}
						}
					}
					zoutmatrix[standard_order(i, j, k, 3, 3, 3)] = kernel(neighborhood);
					z_total_distance += (int)(max_loc - min_loc);
				}
			}
		}
		float finalTime = (float)clock()/CLOCKS_PER_SEC;
		printf("Std time: %f\nZtime: %f\n", midTime-startTime, finalTime-midTime);
		printf("Std Distance: %d\nZdistance: %d\n", std_total_distance, z_total_distance);
		std_total_distance = 0;
		z_total_distance = 0;
	}
}
