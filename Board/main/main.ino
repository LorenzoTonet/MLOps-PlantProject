#include <math.h>
#include <stdlib.h>

// Inclusion of library for working with temperature sensor.
#include <DHT.h>

// Definition of sensor type.
#define DHT_SENSOR_TYPE DHT11
#define WINDOW_SIZE 6

// Output periodicity (In intervals of 10 seconds)
// = one log every five minutes
static const int PERIODICITY = 5 * 6;

// Pin definition
static const int DHT_SENSOR_PIN = 22;
static const int LIGHT_SENSOR_PIN = A0;
static const int SOIL_SENSOR_PIN = A1;
static const int DRY_WARNING_PIN = 7;

// Setup 
DHT dht(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);


typedef struct Window {
    int Nobs;
    int cpos;
    double * vals;
};

// Variable definitions
int counter;
float temp_temperature = 0;
float temp_humidty = 0;
double light_sensor_value;
double temp_sensor_value;
double humid_sensor_value;
double soil_humid_sensor_value;

Window * light_sensor_window;
Window * temp_sensor_window;
Window * air_humid_sensor_window;
Window * soil_humid_sensor_window;


// Function to create a new Window
Window * newWind(int Nobs)
{
    // Allocate space for the struct and the value vector
    Window * wind = (Window *) malloc(sizeof(Window));
    double * vals = (double *) malloc(sizeof(double) * Nobs);
    // Initialize the array to zero
    for (int i = 0; i < Nobs; i++)
        vals[i] = 0.0;
    // Fill the elements
    wind->Nobs = Nobs;
    wind->cpos = 0;
    wind->vals = vals;
    // Return the filled struct
    return wind;
}

// Function to add an observation to the window
void addObsWind(Window * wind, double value)
{
    int cpos = wind->cpos;
    int Nobs = wind->Nobs;

    cpos = (cpos + 1) % Nobs;
    wind->cpos = cpos;

    (wind->vals)[cpos] = value;
}

// Function to calculate the moving average
double averageWind(Window * wind)
{
    double mean = 0;
    int Nobs = wind->Nobs;
    double * vals = wind->vals;

    for (int i = 0; i < Nobs; i++)
        mean += vals[i];

    return mean / (Nobs);
}

// Calculate the standard deviation in the interval
double sdWind(Window * wind)
{
    double mean = 0;
    double sd = 0;
    double curr;
    int Nobs = wind->Nobs;
    double * vals = wind->vals;

    for (int i = 0; i < Nobs; i++)
        mean += vals[i];

    mean /= Nobs;

    for (int i = 0; i < Nobs; i++)
    {
        curr = (vals[i] - mean);
        sd += curr * curr;
    }

    sd /= Nobs;
    sd = sqrt(sd);

    return sd;
}

double maxWind(Window * wind)
{
    int Nobs = wind->Nobs;
    double * vals = wind->vals;
    double maximum = vals[0];

    for (int i = 1; i < Nobs; i++)
        maximum = max(vals[i], maximum);

    return maximum;
}

double minWind(Window * wind)
{
    int Nobs = wind->Nobs;
    double * vals = wind->vals;
    double minimum = vals[0];

    for (int i = 1; i < Nobs; i++)
        minimum = min(vals[i], minimum);

    return minimum;
}


void serialPrintWindow(Window * wind, int digits)
{
    Serial.print(averageWind(wind), digits); // Print with precision to help with debugging
    Serial.print(",");
    Serial.print(sdWind(wind), digits);
    Serial.print(",");
    Serial.print(maxWind(wind), digits);
    Serial.print(",");
    Serial.print(minWind(wind), digits);
}


void setup()
{
    pinMode(DHT_SENSOR_PIN, INPUT);
    pinMode(LIGHT_SENSOR_PIN, INPUT);
    pinMode(SOIL_SENSOR_PIN, INPUT);
    pinMode(DRY_WARNING_PIN, OUTPUT);

    Serial.begin(115200);
    Serial.setTimeout(10);

    counter = 0;

    light_sensor_window      = newWind(WINDOW_SIZE);
    temp_sensor_window       = newWind(WINDOW_SIZE);
    air_humid_sensor_window  = newWind(WINDOW_SIZE);
    soil_humid_sensor_window = newWind(WINDOW_SIZE);
    
    dht.begin();
    delay(2000);
}

void loop()
{
    // Increment current iteration counter
    counter++;

    // Read a value from the sensors from the respective pins
    light_sensor_value      = 1023 - analogRead(LIGHT_SENSOR_PIN);
    soil_humid_sensor_value = 1023 - analogRead(SOIL_SENSOR_PIN);

    // Write to the variables the current value of humidity and temperature
    temp_sensor_value = (double) dht.readTemperature();
    humid_sensor_value = (double) dht.readHumidity();

    // Humidity warning
    if (soil_humid_sensor_value < 250)
    {
        digitalWrite(DRY_WARNING_PIN, counter % 2);
    } else {
        digitalWrite(DRY_WARNING_PIN, 0);
    }


    // Add observations to the respective windows
    addObsWind(light_sensor_window, light_sensor_value);
    addObsWind(temp_sensor_window, temp_sensor_value);
    addObsWind(air_humid_sensor_window, humid_sensor_value);
    addObsWind(soil_humid_sensor_window, soil_humid_sensor_value);

    // Print to the serial terminal the statistics
    // In order for each of the sensors (LIGHT, TEMPERATURE, AIR HUMIDITY and SOIL HUMIDITY)
    // are collected and printed to the serial terminal separated by commas and terminated
    // by a newline character:
    //  - Sensor value in that instant
    //  - Mean over the window
    //  - Standard deviation over the window
    //  - Maximum of the Window
    //  - Minimum of the Window

    // This means a certain time has passed
    // So we output
    if (counter == PERIODICITY)
    {
        counter = 0;

        // Print plant ID, currently a placeholder.
        Serial.print("1,");

        Serial.print(light_sensor_value, 8);
        Serial.print(",");
        serialPrintWindow(light_sensor_window, 8);
        Serial.print(",");

        Serial.print(temp_sensor_value, 8);
        Serial.print(",");
        serialPrintWindow(temp_sensor_window, 8);
        Serial.print(",");

        Serial.print(humid_sensor_value, 8);
        Serial.print(",");
        serialPrintWindow(air_humid_sensor_window, 8);
        Serial.print(",");

        Serial.print(soil_humid_sensor_value, 8);
        Serial.print(",");
        serialPrintWindow(soil_humid_sensor_window, 8);

        // End of the line
        Serial.println();
    }
    
    // Test if this is the problem for the temperature and humidiy read
    delay(1000 * 10);
}
