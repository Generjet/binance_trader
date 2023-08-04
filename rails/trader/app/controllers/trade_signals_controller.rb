class TradeSignalsController < ApplicationController
  before_action :set_trade_signal, only: %i[ show edit update destroy ]

  # GET /trade_signals or /trade_signals.json
  def index
    @trade_signals = TradeSignal.all
  end

  # GET /trade_signals/1 or /trade_signals/1.json
  def show
  end

  # GET /trade_signals/new
  def new
    @trade_signal = TradeSignal.new
  end

  # GET /trade_signals/1/edit
  def edit
  end

  # POST /trade_signals or /trade_signals.json
  def create
    @trade_signal = TradeSignal.new(trade_signal_params)

    respond_to do |format|
      if @trade_signal.save
        format.html { redirect_to trade_signal_url(@trade_signal), notice: "Trade signal was successfully created." }
        format.json { render :show, status: :created, location: @trade_signal }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @trade_signal.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /trade_signals/1 or /trade_signals/1.json
  def update
    respond_to do |format|
      if @trade_signal.update(trade_signal_params)
        format.html { redirect_to trade_signal_url(@trade_signal), notice: "Trade signal was successfully updated." }
        format.json { render :show, status: :ok, location: @trade_signal }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @trade_signal.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /trade_signals/1 or /trade_signals/1.json
  def destroy
    @trade_signal.destroy

    respond_to do |format|
      format.html { redirect_to trade_signals_url, notice: "Trade signal was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_trade_signal
      @trade_signal = TradeSignal.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def trade_signal_params
      params.require(:trade_signal).permit(:date, :rsi, :k, :d, :macd, :support, :resistance, :buy_zone, :sell_zone, :currency, :bot_signal, :last_close_price)
    end
end
