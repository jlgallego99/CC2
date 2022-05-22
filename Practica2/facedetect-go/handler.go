package function

import (
	"io/ioutil"
	"net/http"
)

// Handle a serverless request
func Handle(req []byte) string {
	// Sacar la imagen de la URL
	response, err := http.Get(string(req))
	if err != nil {
		return err.Error()
	}
	defer response.Body.Close()

	var image []byte
	image, err = ioutil.ReadAll(response.Body)
	if err != nil {
		return err.Error()
	}

	return string(image)
}
