package matchmaker

import (
	"testing"
)

func TestGenerateKnockoutRound(t *testing.T) {
	contestants := []Contestant{
		{ID: 101, Seed: 1, Name: "Trader Alpha"},
		{ID: 102, Seed: 2, Name: "Trader Beta"},
		{ID: 103, Seed: 3, Name: "Trader Gamma"},
		{ID: 104, Seed: 4, Name: "Trader Delta"},
	}

	matches, err := GenerateKnockoutRound(contestants, 1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(matches) != 2 {
		t.Fatalf("expected 2 matches, got %d", len(matches))
	}

	// Match 1: Seed 1 vs Seed 4
	if matches[0].Player1.Seed != 1 || matches[0].Player2.Seed != 4 {
		t.Errorf("match 1 incorrect pairing: %+v", matches[0])
	}

	// Match 2: Seed 2 vs Seed 3
	if matches[1].Player1.Seed != 2 || matches[1].Player2.Seed != 3 {
		t.Errorf("match 2 incorrect pairing: %+v", matches[1])
	}
}
