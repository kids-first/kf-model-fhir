
RESULT=false
SUCCESS_STR="Overall result: SUCCESS"

if [[ -z $1 ]] || [[ -z $2 ]]; then
    echo "You must provide the path to the directory containing the fhir
profiles and the file name of the profile to validate. Exiting with code 1"
    exit 1
fi

echo "Begin torinox validation for profile"
cd "$1"

alias torinox="~/.dotnet/tools/fhir"

torinox clear
torinox push "$2"
torinox peek
LOG=$(torinox validate)
echo $LOG
RESULT=$(echo "$LOG" | grep "$SUCCESS_STR")

if [[ $RESULT != $SUCCESS_STR ]]; then
    exit 1
fi

cd -
echo "End torinox validation"
