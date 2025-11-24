import java.nio.file.Files
import java.nio.file.Paths

def csvPath = "parameter_files/plan_params.csv"
def file = new File(csvPath)

if (file.exists()) {

    def lines = file.readLines()

    // For each line, split by comma and set variables
    lines.eachWithIndex { line, idx ->
        def values = line.split(",")
        log.info("here1")

        // Set each value as a variable, e.g. param_0_0, param_0_1, ...
        values.eachWithIndex { val, col ->
            vars.put("param_${idx}_${col}", val)
        }
    }
}

def pp_endpoint = vars.get("param_0_0")
def pp_apim_env = vars.get("param_0_1")
def pp_apikey = vars.get("param_0_2")
def pp_kid = vars.get("param_0_3")

def serviceendpoint = props.get("serviceendpoint")
if (serviceendpoint == null || serviceendpoint == "") {
    serviceendpoint = pp_endpoint
}
vars.put("ServiceEndpoint", serviceendpoint)


def kid = props.get("kid")
if (kid == null || kid == "") {
  kid = pp_kid
}
vars.put("Kid", kid)


def Apim_Env = props.get("apim_env")
if (Apim_Env == null || Apim_Env == "") {
    Apim_Env = pp_apim_env
}
vars.put("Apim_Env", Apim_Env)

def apikey = props.get("apikey")
if (apikey == null || apikey == "") {
    apikey = pp_apikey
}
vars.put("ApiKey", apikey)



