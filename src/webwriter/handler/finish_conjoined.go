package handler

import (
	"fmt"
	"log"
	"net/http"

	"tools"
	"types"
	"unifiedid"

	"webwriter/req"
	"webwriter/writers"
)

func FinishConjoined(
	responseWriter http.ResponseWriter,
	request *http.Request,
	parsedRequest req.ParsedRequest,
	collectionRow types.CollectionRow,
	unifiedIDChannel unifiedid.UnifiedIDChan,
	deliverator tools.Deliverator,
	dataWriterClientChans []writers.DataWriterClientChan) error {

	log.Printf("debug: %s; %s %s %s %d", parsedRequest.Type,
		parsedRequest.RequestID, parsedRequest.CollectionName,
		parsedRequest.Key, parsedRequest.UnifiedID)

	return fmt.Errorf("%s not Implemented", parsedRequest.Type)
}