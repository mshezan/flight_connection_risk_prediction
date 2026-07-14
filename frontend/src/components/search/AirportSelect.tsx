import { useState } from "react";
import { Check, ChevronsUpDown } from "lucide-react";

import airports from "@/data/airports.json";

import { Button } from "@/components/ui/button";

import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface Airport {
  code: string;
  city: string;
  state: string;
  name: string;
  display: string;
}

interface AirportSelectProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export default function AirportSelect({
  value,
  onChange,
  placeholder = "Select airport",
}: AirportSelectProps) {
  const [open, setOpen] = useState(false);

  const selectedAirport = (
    airports as Airport[]
  ).find(
    (airport) => airport.code === value
  );

  return (
    <Popover
      open={open}
      onOpenChange={setOpen}
    >
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="   h-14 w-full
                        justify-between
                        rounded-xl
                        border-[#2a3950]
                        bg-[#0c182a]
                        px-4
                        font-normal
                        text-white
                        hover:bg-[#101e33]
                        hover:text-white
                        data-[state=open]:border-[#6f63e8]
                        data-[state=open]:bg-[#101e33]
                        "
        >
          <span className="truncate">
            {selectedAirport
              ? selectedAirport.display
              : placeholder}
          </span>

          <ChevronsUpDown className="ml-2 size-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>

      <PopoverContent
        className="
            w-[var(--radix-popover-trigger-width)]
            border-[#2a3950]
            bg-[#0c182a]
            p-0
            text-white
        "
        align="start"
        >
        <Command>
          <CommandInput
            placeholder="Search by city, airport, or code..."
          />

          <CommandList>
            <CommandEmpty>
              No airport found.
            </CommandEmpty>

            <CommandGroup>
              {(airports as Airport[]).map(
                (airport) => (
                  <CommandItem
                    key={airport.code}
                    value={`${airport.display} ${airport.name} ${airport.code}`}
                    onSelect={() => {
                      onChange(airport.code);
                      setOpen(false);
                    }}
                  >
                    <Check
                      className={`mr-2 size-4 ${
                        value === airport.code
                          ? "opacity-100"
                          : "opacity-0"
                      }`}
                    />

                    <div className="min-w-0">
                      <p className="truncate font-medium">
                        {airport.display}
                      </p>

                      <p className="truncate text-xs text-muted-foreground">
                        {airport.name}
                      </p>
                    </div>
                  </CommandItem>
                )
              )}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}