package writer

import (
	"testing"

	"tools"

	"datawriter/nodedb"
	"datawriter/types"
)

func TestNewSegment(t *testing.T) {
	if err := nodedb.Initialize(); err != nil {
		t.Fatalf("nodedb.Initialize() %s", err)
	}
	defer nodedb.Close()

	var entry types.SegmentEntry
	entry.CollectionID = 1
	entry.Key = "test key"
	entry.UnifiedID = 2
	entry.Timestamp = tools.Timestamp()
	entry.ConjoinedPart = 0
	entry.SegmentNum = 1
	entry.SourceNodeID = 5
	entry.HandoffNodeID = 0

	var segmentID uint64
	var err error
	if segmentID, err = NewSegment(entry); err != nil {
		t.Fatalf("NewSegment %s", err)
	}
	t.Logf("segment id = %d", segmentID)
}