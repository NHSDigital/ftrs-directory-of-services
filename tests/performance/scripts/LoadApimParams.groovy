import java.nio.file.Files
import java.nio.file.Paths

def csvPath = "parameter_files/apim_params.csv"
def file = new File(csvPath)

if (file.exists()) {

    def lines = file.readLines()

    // For each line, split by comma and set variables
    lines.eachWithIndex { line, idx ->
        def values = line.split(",")

        // Set each value as a variable, e.g. param_0_0, param_0_1, ...
        values.eachWithIndex { val, col ->
            vars.put("param_${idx}_${col}", val)
        }
    }
}

// Set Apim_Env
def Apim_Env = props.get("apim_env")
if (Apim_Env == null || Apim_Env == "") {
    Apim_Env = vars.get("param_0_0")
}
vars.put("Apim_Env", Apim_Env)

// Set Environment
def Env = props.get("env")
if (Env == null || Env == "") {
    Env = vars.get("param_0_1")
}
vars.put("Env", Env)

// Set AWS Secret
def AWS_SECRET_NAME = props.get("AWS_SECRET_NAME")
if (AWS_SECRET_NAME == null || AWS_SECRET_NAME == "") {
    AWS_SECRET_NAME = vars.get("param_0_2")
}
vars.put("AWS_SECRET_NAME", AWS_SECRET_NAME)
