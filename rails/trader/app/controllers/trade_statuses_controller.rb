class TradeStatusesController < ApplicationController
  before_action :set_trade_status, only: %i[ show edit update destroy ]

  # GET /trade_statuses or /trade_statuses.json
  def index
    @trade_statuses = TradeStatus.all
  end

  # GET /trade_statuses/1 or /trade_statuses/1.json
  def show
  end

  # GET /trade_statuses/new
  def new
    @trade_status = TradeStatus.new
  end

  # GET /trade_statuses/1/edit
  def edit
  end

  # POST /trade_statuses or /trade_statuses.json
  def create
    @trade_status = TradeStatus.new(trade_status_params)

    respond_to do |format|
      if @trade_status.save
        format.html { redirect_to trade_status_url(@trade_status), notice: "Trade status was successfully created." }
        format.json { render :show, status: :created, location: @trade_status }
      else
        format.html { render :new, status: :unprocessable_entity }
        format.json { render json: @trade_status.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /trade_statuses/1 or /trade_statuses/1.json
  def update
    respond_to do |format|
      if @trade_status.update(trade_status_params)
        format.html { redirect_to trade_status_url(@trade_status), notice: "Trade status was successfully updated." }
        format.json { render :show, status: :ok, location: @trade_status }
      else
        format.html { render :edit, status: :unprocessable_entity }
        format.json { render json: @trade_status.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /trade_statuses/1 or /trade_statuses/1.json
  def destroy
    @trade_status.destroy

    respond_to do |format|
      format.html { redirect_to trade_statuses_url, notice: "Trade status was successfully destroyed." }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_trade_status
      @trade_status = TradeStatus.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def trade_status_params
      params.require(:trade_status).permit(:period, :trade_status)
    end
end
