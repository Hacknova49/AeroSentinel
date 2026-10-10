"""D4: PyTorch LSTM risk model (needs the [ml] extra). Input: (batch, T, F) feature windows
per zone, e.g. F = [rain, soil_moisture, water_level, elevation, slope]. Output: P(hazard within horizon)."""
from __future__ import annotations

import torch
from torch import nn


class LSTMRiskNet(nn.Module):
    def __init__(self, n_features: int = 5, hidden: int = 64, layers: int = 2, dropout: float = 0.1) -> None:
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, layers, batch_first=True, dropout=dropout)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        return torch.sigmoid(self.head(out[:, -1])).squeeze(-1)


def train(model: LSTMRiskNet, X: torch.Tensor, y: torch.Tensor, epochs: int = 20, lr: float = 1e-3) -> list[float]:
    opt, loss_fn, history = torch.optim.Adam(model.parameters(), lr=lr), nn.BCELoss(), []
    for _ in range(epochs):
        opt.zero_grad()
        loss = loss_fn(model(X), y)
        loss.backward()
        opt.step()
        history.append(loss.item())
    return history
